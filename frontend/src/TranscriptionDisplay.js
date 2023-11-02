import React, { useState, useEffect } from 'react';
import './styles/TranscriptionDisplay.css';
import penIcon from './img/penIcon.svg';


function TranscriptionDisplay() {
  const [fileList, setFileList] = useState([]);
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null); 
  const [speakerMap, setSpeakerMap] = useState({}); 
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const [editingIndex, setEditingIndex] = useState(null); 
  const [tempSpeaker, setTempSpeaker] = useState(""); 
  const [tempText, setTempText] = useState(""); 
  const [editingSegmentIndex, setEditingSegmentIndex] = useState(null);


  const BASE_URL = process.env.REACT_APP_BACKEND_URL;
  // Fetch the list of files when the page loads
  useEffect(() => {
    console.log(process.env.REACT_APP_BACKEND_URL);
    const fetchFileList = async () => {
      try {
        const response = await fetch(`http://${BASE_URL}/media`);
        if (response.ok) {
          const data = await response.json();
          setFileList(data.message);
        }
      } catch (error) {
        console.error('Error fetching file list.', error);
      }
    };

    fetchFileList();
  }, [BASE_URL]);

  // Fetch the content of a file when clicked
  const fetchFileContent = async (mediaId) => {
    try {
      const response = await fetch(`http://${BASE_URL}/media/${mediaId}/analysis`);
      if (response.ok) {
        const data = await response.json();  // First parse the entire JSON response
        const segments = data.message.diarization.segments;  // Then access the required properties
        setTranscriptionData(segments);
        setSelectedFile(mediaId);
      }
    } catch (error) {
      console.error('Error fetching file content.', error);
    }
};

const uploadTranscriptionEdits = async (mediaId) => {
  const payload = {
    "diarization.segments": transcriptionData
  };
  console.log(JSON.stringify(payload))
  try {
    const response = await fetch(`http://${BASE_URL}/media/${mediaId}/analysis`, {
      method: 'PUT', // or 'POST' if you are creating a new entry
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Handle a successful response
    const result = await response.json();
    console.log('Success:', result);
  } catch (error) {
    console.error('Error uploading transcription edits:', error);
  }
};

const startEditing = (index, speaker, text) => {
  setEditingSegmentIndex(index); // Set the index of the segment being edited
  setTempSpeaker(speaker);
  setTempText(text);
};

const startEditingBlock = (index, speaker, text) => {
  setEditingIndex(index);
  setTempSpeaker(speaker);
  setTempText(text);
};

const saveText = (index) => {
  // Save the text to your state or backend
  const updatedTranscriptionData = [...transcriptionData];
  updatedTranscriptionData[index] = { ...updatedTranscriptionData[index], text: tempText, speaker: tempSpeaker};
  setTranscriptionData(updatedTranscriptionData);
  setEditingIndex(null);
};

const handleChangeCurrentSpeakerLabelConfirm = () => {
  if (tempSpeaker.trim()) {
    const updatedTranscriptionData = transcriptionData.map((segment, index) => {
      if (index === editingSegmentIndex) {
        return { ...segment, speaker: tempSpeaker };
      }
      return segment;
    });
    setTranscriptionData(updatedTranscriptionData);
    setEditingSegmentIndex(null); // Exit editing mode after updating the map
  }
};

const handleChangeAllSpeakerLabelsConfirm = () => {
  if (tempSpeaker.trim()) {
    const updatedTranscriptionData = transcriptionData.map(segment => {
      if (segment.speaker === transcriptionData[editingSegmentIndex].speaker) {
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
    const minutes = Math.floor(roundedSeconds / 60).toString().padStart(2, '0');
    const remainingSeconds = (roundedSeconds % 60).toString().padStart(2, '0');
    return `${minutes}.${remainingSeconds}`;
  };
  
  let previousSpeaker = null;

  return (
    <div className="Display">
      

      <h1>Transcription App</h1>
      {!selectedFile && (
        <div>
          <h2>Available Files</h2>
          <ul className="file-list">
            {fileList.map(file => (
              <li key={file._id} onClick={() => fetchFileContent(file._id)}>
                {file.name}
              </li>
            ))}
          </ul>
        </div>
      )}

<div>
{selectedFile && (
      <button onClick={() => uploadTranscriptionEdits(selectedFile)} className="save-button">
        Save Changes
      </button>
    )}
  {transcriptionData && transcriptionData.map((item, index) => {
    
    const currentSpeaker = speakerMap[item.speaker] || item.speaker;
    const showSpeaker = currentSpeaker !== previousSpeaker;
    previousSpeaker = currentSpeaker;
    return (
      <div key={index} className="transcription-item">
        {showSpeaker && (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h3>{currentSpeaker}:</h3>
            <button className="edit-button" onClick={() => startEditing(index, item.speaker, item.text)}>
              <img src={penIcon} alt="Edit" width="16" height="16" />
            </button>
            {editingSegmentIndex === index && (
            <>
              <input
                className="label-input"
                value={tempSpeaker}
                onChange={(e) => setTempSpeaker(e.target.value)}
              />
              <button className="change-label-button" onClick={() => handleChangeCurrentSpeakerLabelConfirm()}>
                Change this label
              </button>
              <button className="change-label-button" onClick={() => handleChangeAllSpeakerLabelsConfirm(tempSpeaker)}>
                Change all labels
              </button>
            </> 
          )}
          </div>
        )}
        <p className="transcription-text"
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
        onKeyDown={(e) => e.key=='Enter' && saveText(index)}
      />
      <div className='speaker-tag'>speaker: </div>
      
      <input
                className="text-input-label"
                value={tempSpeaker}
                onChange={(e) => setTempSpeaker(e.target.value)}

                onKeyDown={(e) => e.key=='Enter' && saveText(index)}
              />    
      </>
    ) : (
      <span>{item.text}</span>
    )}
    {hoveredIndex === index && editingIndex !== index && (
      <button 
        className="edit-button-style" 
        onClick={() => startEditingBlock(index, item.speaker, item.text)}
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
