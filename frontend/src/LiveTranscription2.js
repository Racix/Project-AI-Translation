import React, { useState, useRef, useEffect } from 'react';
import "./styles/TranscriptionDisplay.css";

const LiveTranscription = () => {
  const [roomId, setRoomId] = useState('');
  const [socket, setSocket] = useState(null);
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesRef = useRef(null);

  const BASE_URL = "130.240.200.128:8080";

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
      handleTranscriptionData(data.transcription.segments);
    };
  };

  const handleTranscriptionData = (segments) => {
    setTranscriptionData((prevData) => [...prevData, ...segments]);
  };

  // Scroll to the bottom of the messages whenever new messages are added
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [transcriptionData]);

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  return (
    <div className="Display">
      <div className="chat-container">
        <div className="chat-messages" ref={messagesRef}>
          {transcriptionData.map((item, index) => (
            <div key={index} className="transcription-item">
              <p className="transcription-text">
                <span>{item.text}</span>
              </p>
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <button className='blue-button' onClick={connectToWebSocket}>Connect to WebSocket</button>
        </div>
      </div>
    </div>
  );
};

export default LiveTranscription;
