import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./styles/Upload.css";

function Upload() {
  const [file, setFile] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [fileName, setFileName] = useState("No file chosen");
  const [data, setData] = useState(null);
  const [chosenFileID, setChosenFileID] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchFileList();
  }, [BASE_URL]);

  const fetchFileList = async () => {
    try {
      const response = await fetch(`http://${BASE_URL}/media`);
      if (response.ok) {
        const data = await response.json();
        setFileList(data.message);
      }
    } catch (error) {
      console.error("Error fetching file list.", error);
    }
  };

  const startAnalysisRequest = async (mediaId) => {
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
        alert("Error uploading file!");
      }
    } catch (error) {
      console.error("Error fetching file content.", error);
    }
  };

  const processFile = async (mediaId) => {
    const ws = new WebSocket(`ws://${BASE_URL}/ws/analysis/${mediaId}`);

    ws.onopen = () => {
      console.log("WebSocket connected!");
      startAnalysisRequest(mediaId);
    };

    ws.onmessage = (event) => {
      const receivedData = JSON.parse(event.data);
      setData(receivedData); // Process the received data as needed
      console.log(receivedData);
      console.log(receivedData.status);
      if (receivedData.status === 201) {
        ws.close();
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
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

  const handleClick = (fileId) => {
    if (isDisabled) {
      return;
    }
    setIsDisabled(true);
    setChosenFileID(fileId);
    processFile(fileId);
  };

  const onUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`http://${BASE_URL}/media`, {
        method: "POST",
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
        <button onClick={onUpload} className="upload-button">
          Upload
        </button>
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
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Upload;
