import React, { useState, useEffect } from 'react';
import "./styles/TranscriptionDisplay.css";
import ChatContainer from "./ChatContainer";
// import "./styles/test.css";


const LiveTranscription = () => {
  const [roomId, setRoomId] = useState('');
  const [socket, setSocket] = useState(null);
  const [transcriptionData, setTranscriptionData] = useState([]);
  const [oldTranscriptionData, setOldTranscriptionData] = useState([]);
  const [newTranscriptionData, setNewTranscriptionData] = useState([]);

//   const BASE_URL = process.env.REACT_APP_BACKEND_URL;
  const BASE_URL = "130.240.200.128:8080";

  useEffect(() => {

    setTranscriptionData(prevData => {
      console.log("prev", prevData)
      console.log("copy: ", oldTranscriptionData)
      const data = [...prevData].concat(oldTranscriptionData); // Create a copy of the previous data
      let lastIndex = data.length - 1;
      const startOfNewData = newTranscriptionData[0].start;

      console.log("DATA")
      data.map((item, index) => (
        console.log(item.start, " : ", item.duration, " : ", item.text)
      ))
      console.log("NEWDATA")
      newTranscriptionData.map((item, index) => (
        console.log(item.start, " : ", item.duration, " : ", item.text)
      ))
      // console.log("arr före loop: |", data, " : ", newData)

      while (lastIndex >= 0 && data[lastIndex].start >= startOfNewData) {
        // if (lastIndex >= 0) {
        //   console.log("tider : " , startOfNewData, " : ", data[lastIndex].start) 
        // }
        data.pop();
        lastIndex = data.length - 1;
      }

      // const res = data.concat(newData.transcription.segments)
      // console.log("RES")
      // res.map((item, index) => (
      //   console.log(item.start, " : ", item.duration, " : ", item.text)
      // ))
  
      // Concatenate the new data to the existing data
      return data;
    });
    
  }, [newTranscriptionData, oldTranscriptionData]);

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
      console.log("nD", newTranscriptionData);
      handleTranscriptionData(data, newTranscriptionData);
      // Handle incoming messages from the WebSocket
    };
  };

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  const handleTranscriptionData = (newData) => {
    console.log("old: ")
    if(newData === null){
      console.error("recieved null")
      return;
    }
    setOldTranscriptionData(newTranscriptionData);

    console.log("här borde nD sättas: ", newData.transcription.segments)
    setNewTranscriptionData(newData.transcription.segments);
    
    // const data = transcriptionData;
    // console.log("arr före loop: |")
    // let lastIndex = data.length -1;
    // console.log("lasti:", transcriptionData) 
    // const startOfNewData = newData.transcription.segments[0].start
    // // console.log("tider: " , startOfNewData, " : ", data[lastIndex].start) 
    // while (lastIndex>0 && data[lastIndex].start > startOfNewData) {
    //   console.log("tider: " , startOfNewData, " : ", data[lastIndex].start) 
    //   data.pop();
    //   lastIndex = data.length - 1;
    // }
    // // console.log("sluttider:", startOfNewData, " : ", data[lastIndex].start);
    // setTranscriptionData(data.concat(newData.transcription.segments))
  }

  const dataArrayToString = (transcriptionData) => {
    let newTransData = "";
    transcriptionData.map((item, index) => (
      newTransData = newTransData.concat(item.text)
    ))
    return newTransData;
  }

  const myNewData = "tjena";

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
          {/* Additional UI elements for sending messages */}

        </div>
        <div>
          <ChatContainer messages={transcriptionData} />
        </div>

        <div className="transcription-item">
          <p className="transcription-text">
            <span>
              {dataArrayToString(transcriptionData)} +
              <span style={{ backgroundColor: 'red' ,padding: '0 5px'}}>
                {dataArrayToString(newTranscriptionData)}
              </span>
            </span>
          </p>
        </div>
        {/* { transcriptionData.map((item, index) => (
          <div key={index} className="transcription-item">
            <p className="transcription-text">
              <span>{item.text}</span>
            </p>
          </div>
        ))} */}
      </div>
    </div>
  );
};

export default LiveTranscription;