import React, { useState, useRef } from 'react';
import "./styles/TranscriptionDisplay.css";

const LiveTranscription = () => {
  const [roomId, setRoomId] = useState('');
  const [transcriptionData, setTranscriptionData] = useState([]);
  const scrollRef = useRef(null);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL;

  const connectToWebSocket = () => {
    const socket = new WebSocket(`ws://${BASE_URL}/ws/live-transcription/${roomId}`);

    socket.onopen = () => {
      setTranscriptionData([]);
      alert("Connected to room")
      console.log('WebSocket connected');
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      handleTranscriptionData(data);
    };
  };

  const handleTranscriptionData = (newData) => {
    if(newData === null){
      console.error("Recieved null on new transcription data from server")
      return;
    }

    setTranscriptionData(prevData => {
      const data = [...prevData]; // Create a copy of the previous data
      let newSegments = newData.transcription.segments;

      if (newSegments.length > 0) {
        let lastIndex = data.length - 1;
        const startOfNewData = newSegments[0].start;
        // Remove old data until starttime lines up
        while (lastIndex >= 0 && data[lastIndex].start >= startOfNewData) {
          data.pop();
          lastIndex--;
        }
        // Fallback to remove from new data if it still overlapps (to try and remove repeting scentences)
        while (lastIndex >= 0 && newSegments.length > 0 && data[lastIndex].start + data[lastIndex].duration > newSegments[0].start) {
          console.log("need shift data. old start ",  data[lastIndex].start, " old start + dur ",  data[lastIndex].start + data[lastIndex].duration, " new start ", newSegments[0].start)
          newSegments.shift();
        }
      }

      return data.concat(newSegments);
    });
  }

  const dataArrayToString = (transcriptionData) => {
    let newTransData = "";
    transcriptionData.map((item, index) => (
      newTransData = newTransData.concat(item.text)
    ))
    
    //scroll the window down
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }

    return newTransData;
  }

  return (
    <div className="Display">
      <div className="upload-container">
        <div className="file-input-container">
          <input
              className="label-input"
              type="text"
              placeholder="Enter Room ID"
              value={roomId}
              onChange={(e) => setRoomId(e.target.value)}
          />
          <button className='blue-button' onClick={connectToWebSocket}>Connect to Room id</button>
        </div>
        <div ref={scrollRef} className="transcription-item" style={{width: "80%", maxHeight: "150px", overflow: "hidden", overflowY: "scroll", backgroundColor: "white"}}>
          <p className="transcription-text" style={{margin: "0"}}>
            <span>{
            dataArrayToString(transcriptionData)}</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LiveTranscription;