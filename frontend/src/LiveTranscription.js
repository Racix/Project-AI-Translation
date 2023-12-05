import React, { useState } from 'react';
import "./styles/TranscriptionDisplay.css";

const LiveTranscription = () => {
  const [roomId, setRoomId] = useState('');
  const [socket, setSocket] = useState(null);
  const [transcriptionData, setTranscriptionData] = useState([]);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;

  const connectToWebSocket = () => {
    const newSocket = new WebSocket(`ws://${BASE_URL}/ws/live-transcription/${roomId}`);
    setSocket(newSocket);

    newSocket.onopen = () => {
      console.log('WebSocket connected');
    };

    newSocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      handleTranscriptionData(data);
    };
  };

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  const handleTranscriptionData = (newData) => {
    if(newData === null){
      console.error("recieved null")
      return;
    }
    setTranscriptionData(prevData => {
      const data = [...prevData]; // Create a copy of the previous data
      let lastIndex = data.length - 1;
      const startOfNewData = newData.transcription.segments[0].start;

      while (lastIndex >= 0 && data[lastIndex].start >= startOfNewData) {

        data.pop();
        lastIndex = data.length - 1;
      }

      return data.concat(newData.transcription.segments);
    });
  }

  const dataArrayToString = (transcriptionData) => {
    let newTransData = "";
    transcriptionData.map((item, index) => (
      newTransData = newTransData.concat(item.text)
    ))
    return newTransData;
  }

  return (
    <div className="Display">
      <div className="upload-container">
        <div className="file-input-container">
          <input
              type="text"
              placeholder="Enter Room ID"
              value={roomId}
              onChange={(e) => setRoomId(e.target.value)}
          />
          <button className='blue-button' onClick={connectToWebSocket}>Connect to WebSocket</button>
        </div>
        <div className="transcription-item">
          <p className="transcription-text">
            <span>{dataArrayToString(transcriptionData)}</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LiveTranscription;