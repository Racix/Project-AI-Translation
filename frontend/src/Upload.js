import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./styles/Upload.css";
import logo from './img/Doris_logo.png'

function Upload() {
  const [file, setFile] = useState(null);
  const [speakers, setSpeakers] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [label, setLabel] = useState([]);
  const [info, setInfo] = useState([]);
  const [fileName, setFileName] = useState("No file chosen");
  const [data, setData] = useState(null);
  const [chosenFileID, setChosenFileID] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);
  const labelsAsString ='['+ label.map(label => `{"${label.name}":"${label.description}"}`) + ']';//JSON.stringify(label);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;

  const imageStyle = {
    listStyle: 'none',
    padding: '25px 0 25px 85px',
    backgroundImage: 'url('+logo+')',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'left center',
    backgroundSize: '80px',
  };

  useEffect(() => {
    fetchFileList();
  }, [BASE_URL]);

  const fetchFileList = async () => {
    try {
      const response = await fetch(`http://${BASE_URL}/media`);
      if (response.ok) {
        const data = await response.json();
        setFileList(data);
      }
    } catch (error) {
      console.error("Error fetching file list.", error);
    }
  };

  const startAnalysisRequest = async (mediaId, ws) => {
    try {
      const formData = new FormData();
      const response = await fetch(
        `http://${BASE_URL}/media/${mediaId}/analysis`,
        {
          method: "POST",
          body: formData,
        }
      );
      if (!response.ok) {
        alert(
          "could not start analysis (if it exists, it needs to be deleted before a new analysis can be done)"
        );
        ws.close();
      }
    } catch (error) {
      console.error("Error fetching file content.", error);
      ws.close();
    }
  };

  const processFile = async (mediaId) => {
    const ws = new WebSocket(`ws://${BASE_URL}/ws/analysis/${mediaId}`);

    ws.onopen = () => {
      console.log("WebSocket connected!");
      setIsDisabled(true);
      startAnalysisRequest(mediaId, ws);
    };

    ws.onmessage = (event) => {
      const receivedData = JSON.parse(event.data);
      setData(receivedData); // Process the received data as needed
      console.log(receivedData);
      console.log(receivedData.status);
      if (receivedData.status !== 200) {
        ws.close();
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
      ws.close();
    };

    ws.onclose = (event) => {
      if (event.wasClean) {
        console.log("WebSocket closed cleanly");
      } else {
        console.error("WebSocket connection died");
      }
      setIsDisabled(false);
    };

    return () => {
      ws.close();
    };
  };

  const deleteMedia = async (mediaId) => {
    try {
      const response = await fetch(`http://${BASE_URL}/media/${mediaId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        console.log("File deleted: ", mediaId);
        fetchFileList();
      }
    } catch (error) {
      console.error("Error deleting file.", error);
    }
  };

  const deleteAnalysis = async (mediaId) => {
    try {
      const response = await fetch(
        `http://${BASE_URL}/media/${mediaId}/analysis`,
        {
          method: "DELETE",
        }
      );
      if (response.ok) {
        console.log("Analysis of deleted: ", mediaId);
        fetchFileList();
      }
    } catch (error) {
      console.error("Error deleting file.", error);
    }
  };

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
    setFileName(
      event.target.files[0] ? event.target.files[0].name : "No file chosen"
    );
  };

  const onSpeakersChange = (event) => {
    const e = event.target.value;
    if (e === "" || /^\d+$/.test(e)) {
      e !== "" && setSpeakers(parseInt(e));
    } else {
      event.target.value = "";
      alert("Invalid input. Please enter an integer!");
    }
  };

  const addLabel = () => {
    const nameInput = document.querySelector('.num-speakers[placeholder="Name"]');
    const descriptionInput = document.querySelector('.num-speakers[placeholder="Description"]');

    if (nameInput.value && descriptionInput.value) {
      const newLabel = {
        name: nameInput.value,
        description: descriptionInput.value,
      };

      setLabel((prevLabels) => [...prevLabels, newLabel]);

      nameInput.value = '';
      descriptionInput.value = '';
    }
  };

  const removeLabel = (indexToRemove) => {
    setLabel((prevLabels) => prevLabels.filter((_, index) => index !== indexToRemove));
  };

  const handleClick = (fileId) => {
    if (isDisabled) {
      return;
    }
    setChosenFileID(fileId);
    processFile(fileId);
  };

  const onUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      var response;

      const baseUrl = `http://${BASE_URL}/media/`;
      const params = new URLSearchParams();

      if (speakers) {
        params.append('speakers', speakers);
      }

      if (label.length > 0) {
        params.append('label', labelsAsString);
      }

      const url = `${baseUrl}${params.toString() ? `?${params.toString()}` : ''}`;

      //const url = `http://${BASE_URL}/media/${speakers ? `?speakers=${speakers}` : ''}${label.length > 0 ? `&label=${labelsAsString}` : ''}`;

      response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert("File uploaded successfully!");
        window.location.reload(); // Reload the entire page
      } else {
        alert("Error uploading file!");
      }
    } catch (error) {
      console.error("There was an error uploading the file.", error);
    }
  };

  const openModal = (listOfInfo) => {
    setInfo(listOfInfo)
    setIsModalVisible(true);
  };

  const closeModal = () => {
    setIsModalVisible(false);
  };

  return (
    <div className="upload-container">
      <div className="file-input-container">
        <input
          type="file"
          onChange={onFileChange}
          className="file-input"
          id="fileInput"
        />
        <label htmlFor="fileInput" className="file-label">
          Browse
        </label>
        <span style={{ marginLeft: "10px" }}>{fileName}</span>
      </div>
      {file && (
        <div className="btn-container label-container">
          <div>
            <h3>Labels:</h3>
            <ul id="labelUl">
              {label.map((label, index) => (
                <li style={imageStyle} key={index}>
                  <span style={{ fontWeight: 'bold' }}>{label.name}</span><br />
                  {label.description}
                  <button className="upload-button" onClick={() => removeLabel(index)}>Remove</button>
                </li>
              ))}
            </ul>
          </div>
          Label:
          <input
            className="num-speakers"
            placeholder="Name"
          />
          <input
            className="num-speakers"
            placeholder="Description"
          />          
          <button onClick={addLabel} className="upload-button">
            Add Label
          </button>
        </div>
      )}
      {file && (
        <div className="btn-container">
          Number of speakers:
          <input
            onChange={onSpeakersChange}
            className="num-speakers"
            placeholder="Nr of Speakers"
          />
          <button onClick={onUpload} className="upload-button">
            Upload
          </button>
        </div>
      )}

      {isModalVisible && (
        <div className="InfoWindow">
          <button onClick={closeModal} className="close-button upload-button">
            Close
          </button>
          <div className="infoContent">
            <h3>Labels:</h3>
            <ul id="labelUl">
              {info.map((info, index) => (
                <li style={imageStyle} key={index}>
                  {Object.entries(info).map(([key, value]) => (
                    <div key={key}>
                    <span style={{ fontWeight: 'bold' }}>{key}</span><br />
                    {value}
                    </div>
                  ))}

                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      <ul className="file-list">
        {fileList.map((file) => (
          <li key={file._id}>
            <Link to={`/display/${file._id}`} className="file-name">
              {file.name}
            </Link>
            {data && chosenFileID === file._id && (
              <div className="message-field">{data.message}</div>
            )}
            <div className="upload-page-buttons-container">
              <button
                onClick={() => deleteMedia(file._id)}
                className="delete-media-button"
              >
                Delete Media
              </button>
              <button
                onClick={() => deleteAnalysis(file._id)}
                className="delete-analysis-button"
              >
                Delete Analysis
              </button>
              <button
                onClick={() => handleClick(file._id)}
                className={`analyze-button ${isDisabled ? "disabled" : ""}`}
                disabled={isDisabled}
              >
                Analyze
              </button>
              <button
                onClick={() => openModal(file.label)}
                className="analyze-button"
              >
                i
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Upload;
