import React, { useState, useEffect } from "react";
import "./styles/TranscriptionDisplay.css";
import penIcon from "./img/penIcon.svg";
import { useParams } from "react-router-dom";
import testfile from "./testfile.json"; //change to your testfile
import Translating from "./Translating";

function TranscriptionDisplay() {
  const [testing] = useState(false); //set to true to use element 'testfile' as outprint (limited functionality)
  const [translating, setTranslating] = useState(false); //true when waiting on a translation to be done, false otherwise
  const { id } = useParams();
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [originalTransData, setOriginalTransData] = useState([]);
  const [summaryData, setSummaryData] = useState("");
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [tempSpeaker, setTempSpeaker] = useState("");
  const [tempText, setTempText] = useState("");
  const [editingSegmentIndex, setEditingSegmentIndex] = useState(null);
  const [textChanged, setTextChanged] = useState(false);
  const [summaryVisible, setSummaryVisible] = useState(false);
  const [data, setData] = useState(null);
  const [buttonClicked, setButtonClicked] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("");
  const [originalLanguage, setOriginalLanguage] = useState("");
  const [isTranslation, setIsTranslation] = useState(false);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;
  const languageMap = { //TODO change to api call asking for available languages
    en: "English",
    sv: "Svenska",
    fi: "suomen kieli",
    fr: "Français",
    es: "Español",
    de: "Deutsch",
    nl: "Nederlands",
    pl: "polski",
    ar: "عربي",
    zh: "中文",
    hi: "हिंदी",
    ru: "Русский",
    
  };
  const languageOptions = Object.entries(languageMap).map(([value, label]) => ({
    value,
    label
  }));

  useEffect(() => {
    fetchFileContent();
  }, [BASE_URL, data, selectedLanguage]);

  const fetchFileContent = async () => {
    if (testing) {
      setTranscriptionData(testfile.message.diarization.segments);
      setOriginalTransData(testfile.message.diarization.segments);
      setSummaryData(testfile.message.summary);
      setTextChanged(false);
      return
    }
    try {
      let endpoint;
      let segmentFrom;
      if (selectedLanguage !== originalLanguage) { 
        endpoint = `http://${BASE_URL}/media/${id}/analysis/translate/${selectedLanguage}`
        segmentFrom = "translation";
      } else {
        endpoint = `http://${BASE_URL}/media/${id}/analysis`
        segmentFrom = "diarization";
      }

      let response = await fetch(endpoint);
      if (!response.ok && selectedLanguage!==originalLanguage) {
        const userResponse = window.confirm("No translation found of , do you want to start a translation? (this might take some time)");

        if (userResponse) {
          // User clicked "OK"
          console.log("User clicked OK");
          setTranslating(true);
        } else {
          // User clicked "Cancel"
          console.log("User clicked Cancel");
          return;
        }
        response = await fetch(endpoint,
          {
            method: "POST",
          }
        )
        setTranslating(false);
      }
      if (response.ok) {
        const data = await response.json(); // First parse the entire JSON response
        const segments = segmentFrom==="diarization" ? data.diarization.segments : [data.translation.segments]; // Then access the required properties
        setTranscriptionData(segments);
        setTextChanged(false);
        setIsTranslation(segmentFrom==="translation");
        if (segmentFrom==="diarization") {
          const summary = data.summary;
          setSummaryData(summary);
          setOriginalTransData(segments);
          setOriginalLanguage(data.diarization["Detected language"]);
        }
      } 
    } catch (error) {
      console.error("Error fetching file content.", error);
    }
  };

  const uploadTranscriptionEdits = async () => {
    const payload = {
      "diarization.segments": transcriptionData,
    };
    try {
      const response = await fetch(
        `http://${BASE_URL}/media/${id}/analysis`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );
      if (response.ok) {
        alert("File saved successfully!");
        setTextChanged(false);
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle a successful response
      const result = await response.json();
      console.log("Success:", result);
    } catch (error) {
      alert("Could not save file");
      console.error("Error uploading transcription edits:", error);
    }
  };

  const startSummarize = async (ws) => {
    try {
      const response = await fetch(
        `http://${BASE_URL}/media/${id}/analysis/summary`,
        {
          method: "POST",
        }
      );
      if (!response.ok) {
        alert("could not start analysis (if it exists, it needs to be deleted before a new analysis can be done)");
        ws.close()
      }
    } catch (error) {
      console.error("Error fetching file content.", error);
      ws.close()
    }
  } 
  const processFile = async () => {
    const ws = new WebSocket(`ws://${BASE_URL}/ws/analysis/${id}`);

    ws.onopen = () => {
      console.log("WebSocket connected!");
      setIsDisabled(true);
      startSummarize(ws);
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
      setSummaryVisible(true)
      setIsDisabled(false);
    };

    return () => {
      ws.close();
    };
  };
  const handleSummaryClick = (fileId) => {
    if (isDisabled) {
      return;
    }
    setButtonClicked(true)
    processFile(fileId);
  };

  const cancelTranscriptionEdits = () => {
    setTextChanged(false)
    setTranscriptionData(originalTransData)
  }

  const unfocusEditingBlocks = () => {
    setEditingIndex(null)
    setEditingSegmentIndex(null);
    setEditingIndex(null);
    setTempSpeaker("");
    setTempText("");

  }

  const startEditing = (index, speaker) => {
    if(index === editingSegmentIndex) {
      unfocusEditingBlocks();
      return
    }
    unfocusEditingBlocks();
    setEditingSegmentIndex(index); // Set the index of the segment being edited
    setTempSpeaker(speaker);
  };

  const startEditingBlock = (index, speaker, text) => {
    unfocusEditingBlocks();
    setEditingIndex(index);
    setTempSpeaker(speaker);
    setTempText(text);
  };

  const saveText = (index) => {
    setTextChanged(true);
    const updatedTranscriptionData = [...transcriptionData];
    updatedTranscriptionData[index] = {
      ...updatedTranscriptionData[index],
      text: tempText,
      speaker: tempSpeaker,
    };
    setTranscriptionData(updatedTranscriptionData);
    setEditingIndex(null);
  };

  const handleChangeCurrentSpeakerLabelConfirm = () => {
    if (tempSpeaker.trim()) {
      const updatedTranscriptionData = transcriptionData.map(
        (segment, index) => {
          if (index === editingSegmentIndex) {
            return { ...segment, speaker: tempSpeaker };
          }
          return segment;
        }
      );
      setTranscriptionData(updatedTranscriptionData);
      setEditingSegmentIndex(null); // Exit editing mode after updating the map
    }
  };

  const handleChangeAllSpeakerLabelsConfirm = () => {
    if (tempSpeaker.trim()) {
      const updatedTranscriptionData = transcriptionData.map((segment) => {
        if (
          segment.speaker === transcriptionData[editingSegmentIndex].speaker
        ) {
          return { ...segment, speaker: tempSpeaker };
        }
        return segment;
      });
      setTranscriptionData(updatedTranscriptionData);
      setEditingSegmentIndex(null); // Exit editing mode after updating all labels
    }
  };

  const formatTime = (seconds) => {
    const roundedSeconds = Math.round(seconds);
    const minutes = Math.floor(roundedSeconds / 60)
      .toString()
      .padStart(2, "0");
    const remainingSeconds = (roundedSeconds % 60).toString().padStart(2, "0");
    return `${minutes}.${remainingSeconds}`;
  };

  const handleLanguageSelection = (event) => {
    const language = event.target.value;
    setSelectedLanguage(language);
  };

  let previousSpeaker = null;

  return (
    <div className="Display">
      <h1>Transcription App</h1>
      {testing &&
       <h2>testing mode is active</h2>
      }
      {translating ? (
        <Translating></Translating>     
      ) : (
        <div>
          <div className="transcription-buttons-container">
            <div>
              {
                summaryData
                ? (
                    // If summaryData is true
                    <button
                      onClick={() => setSummaryVisible(!summaryVisible)}
                      className="summary-button blue-button"
                    >
                      Summary
                    </button>
                  )
                : ( // If false, check if there is transcription
                    transcriptionData.length > 0 && (
                      !buttonClicked ? (
                        <button
                          className="summary-button blue-button"
                          onClick={() => handleSummaryClick()}>
                          Summarize
                        </button>
                      ) : (
                        data && <div className="message-field">{data.message}</div>
                      )
                    )
                )
              }
              {transcriptionData.length > 0 &&
                <select 
                  name="language"
                  className="language-dropdown" 
                  value={selectedLanguage} 
                  onChange={handleLanguageSelection}>
                  <option value="" disabled hidden>Translation</option>
                  <option value={originalLanguage}>{"Original (" + (languageMap[originalLanguage] || originalLanguage) + ")"}</option>
                  {languageOptions.map((option, index) => (
                    option.value !== originalLanguage &&
                    <option key={index} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              }
            </div>
            <div className="text-edit-buttons">
            {textChanged &&
              <button
                onClick={() => cancelTranscriptionEdits()}
                className="cancel-button blue-button"
              >
                Cancel
              </button>
            }
            { textChanged &&
              <button
                onClick={() => uploadTranscriptionEdits()}
                className="save-button blue-button"
              >
                Save Changes
              </button>
            }
            </div>
            
          </div>
          {summaryVisible &&
            <div className="summary-box">
              {summaryData}
            </div>
          }
          {transcriptionData &&
            transcriptionData.map((item, index) => {
              
              const currentSpeaker = item.speaker;
              const showSpeaker = currentSpeaker !== previousSpeaker;
              previousSpeaker = currentSpeaker;
              return (
                isTranslation ? (  
                  <div key={index} className="transcription-item">
                    <p className="transcription-text">
                    <span>{item}</span>
                    </p>
                  </div>
                ) : (
                  <div key={index} className="transcription-item">
                  {showSpeaker && (
                    <div style={{ display: "flex", alignItems: "center" }}>
                      <h3>{currentSpeaker}:</h3>
                      <button
                        className="edit-button"
                        onClick={() =>
                          startEditing(index, item.speaker)
                        }
                      >
                        <img src={penIcon} alt="Edit" width="16" height="16" />
                      </button>
                      {editingSegmentIndex === index && (
                        <>
                          <input
                            className="label-input"
                            value={tempSpeaker}
                            onChange={(e) => setTempSpeaker(e.target.value)}
                          
                          />
                          <button
                            className="change-label-button blue-button"
                            onClick={() =>
                              handleChangeCurrentSpeakerLabelConfirm()
                            }
                          >
                            Change this label
                          </button>
                          <button
                            className="change-label-button blue-button"
                            onClick={() =>
                              handleChangeAllSpeakerLabelsConfirm(tempSpeaker)
                            }
                          >
                            Change all labels
                          </button>
                        </>
                      )}
                    </div>
                  )}
                  <p
                    className="transcription-text"
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                  >
                    <span className="time">{formatTime(item.start)}:</span>

                    {editingIndex === index ? (
                      <>
                        <input
                          className="text-input"
                          value={tempText}
                          onChange={(e) => setTempText(e.target.value)}
                          onKeyDown={(e) => 
                            ((e.key === "Enter") && saveText(index)) ||
                              (e.key === "Escape" && unfocusEditingBlocks())
                                    }
                        />
                        <div className="speaker-tag">speaker: </div>

                        <input
                          className="text-input-label"
                          value={tempSpeaker}
                          onChange={(e) => setTempSpeaker(e.target.value)}
                          onKeyDown={(e) => 
                            ((e.key === "Enter") && saveText(index)) ||
                              (e.key === "Escape" && unfocusEditingBlocks())
                                    }  
                        />
                      </>
                    ) : (
                      <span>{item.text}</span>
                    )}
                    {hoveredIndex === index && editingIndex !== index && (
                      <button
                        className="edit-button-style"
                        onClick={() =>
                          startEditingBlock(index, item.speaker, item.text)
                        }
                      >
                        <img src={penIcon} alt="Edit" width="16" height="16" />
                      </button>
                    )}
                  </p>
                </div>
                )
              );
            })}
        </div>
      )}
    </div>
  );
}

export default TranscriptionDisplay;
