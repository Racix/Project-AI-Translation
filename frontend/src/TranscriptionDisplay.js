import React, { useState, useEffect } from 'react';
import './styles/TranscriptionDisplay.css';
import penIcon from './img/penIcon.svg';


function TranscriptionDisplay() {
  const [fileList, setFileList] = useState([]);
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null); 
  const [speakerMap, setSpeakerMap] = useState({}); 
  const [editingSpeaker, setEditingSpeaker] = useState(null);

  const BASE_URL = process.env.BACKEND_URL;

  // Fetch the list of files when the page loads
  useEffect(() => {
    const fetchFileList = async () => {
      try {
        const response = await fetch(`${BASE_URL}/media`);
        if (response.ok) {
          const data = await response.json();
          setFileList(data.message);
        }
      } catch (error) {
        console.error('Error fetching file list.', error);
      }
    };

    fetchFileList();
  }, []);

  // Fetch the content of a file when clicked
  const fetchFileContent = async (mediaId) => {
    try {
      const response = await fetch(`${BASE_URL}/media/${mediaId}/analysis`);
      if (response.ok) {
        const data = await response.json();  // First parse the entire JSON response
        const segments = data.message.segments;  // Then access the required properties
        console.log(segments)
        setTranscriptionData(segments);
        setSelectedFile(mediaId);
      }
    } catch (error) {
      console.error('Error fetching file content.', error);
    }
};



  const formatTime = (seconds) => {
    const roundedSeconds = Math.round(seconds);
    const minutes = Math.floor(roundedSeconds / 60).toString().padStart(2, '0');
    const remainingSeconds = (roundedSeconds % 60).toString().padStart(2, '0');
    return `${minutes}.${remainingSeconds}`;
  };

  const handleLabelChange = (originalSpeaker, newLabel) => {
    setSpeakerMap(prevState => ({
      ...prevState,
      [originalSpeaker]: newLabel
    }));
    setEditingSpeaker(null); // Close the input after editing
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
  {transcriptionData.map((item, index) => {
    const currentSpeaker = speakerMap[item.speaker] || item.speaker;
    const showSpeaker = currentSpeaker !== previousSpeaker;
    previousSpeaker = currentSpeaker;
    return (
      <div key={index} className="transcription-item">
        {showSpeaker && (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h3>{currentSpeaker}:</h3>
            <button className="edit-button" onClick={() => setEditingSpeaker(item.speaker)}>
              <img src={penIcon} alt="Edit" width="16" height="16" />
            </button>

            {editingSpeaker === item.speaker && (
              <input
                className="label-input"
                defaultValue={currentSpeaker}
                onBlur={(e) => handleLabelChange(item.speaker, e.target.value)}
              />
            )}
          </div>
        )}
        <p><span className="time">{formatTime(item.start)}:</span> {item.text}</p>
      </div>
    );
  })}
</div>
    </div>
  );
}

export default TranscriptionDisplay;
