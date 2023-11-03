import React, { useState, useEffect } from "react";
import "./styles/TranscriptionDisplay.css";
import penIcon from "./img/penIcon.svg";
import { useParams } from "react-router-dom";

function TranscriptionDisplay() {
  const { id } = useParams();
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [speakerMap, setSpeakerMap] = useState({});
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const [editingIndex, setEditingIndex] = useState(null);
  const [tempSpeaker, setTempSpeaker] = useState("");
  const [tempText, setTempText] = useState("");
  const [editingSegmentIndex, setEditingSegmentIndex] = useState(null);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchFileContent();
  }, [BASE_URL]);

  const fetchFileContent = async () => {
    try {
      const response = await fetch(
        `http://${BASE_URL}/media/${id}/analysis`
      );
      if (response.ok) {
        const data = await response.json(); // First parse the entire JSON response
        const segments = data.message.diarization.segments; // Then access the required properties
        setTranscriptionData(segments);
      }
    } catch (error) {
      console.error("Error fetching file content.", error);
    }
  };

  const uploadTranscriptionEdits = async () => {
    const payload = {
      "diarization.segments": transcriptionData,
    };
    console.log(JSON.stringify(payload));
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
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle a successful response
      const result = await response.json();
      console.log("Success:", result);
    } catch (error) {
      console.error("Error uploading transcription edits:", error);
    }
  };

  const unfocusEditingBlocks = () => {
    setEditingSegmentIndex(null)
    setEditingIndex(null)

  }

  const startEditing = (index, speaker) => {
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

  let previousSpeaker = null;

  return (
    <div className="Display">
      <h1>Transcription App</h1>
      <div>
        <button
          onClick={() => uploadTranscriptionEdits()}
          className="save-button"
        >
          Save Changes
        </button>
        {transcriptionData &&
          transcriptionData.map((item, index) => {
            const currentSpeaker = speakerMap[item.speaker] || item.speaker;
            const showSpeaker = currentSpeaker !== previousSpeaker;
            previousSpeaker = currentSpeaker;
            return (
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
                          className="change-label-button"
                          onClick={() =>
                            handleChangeCurrentSpeakerLabelConfirm()
                          }
                        >
                          Change this label
                        </button>
                        <button
                          className="change-label-button"
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
                          ((e.key == "Enter") && saveText(index)) ||
                            e.key == "Escape" && unfocusEditingBlocks()
                                  }
                      />
                      <div className="speaker-tag">speaker: </div>

                      <input
                        className="text-input-label"
                        value={tempSpeaker}
                        onChange={(e) => setTempSpeaker(e.target.value)}
                        onKeyDown={(e) => 
                          ((e.key == "Enter") && saveText(index)) ||
                            e.key == "Escape" && unfocusEditingBlocks()
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
            );
          })}
      </div>
    </div>
  );
}

export default TranscriptionDisplay;
