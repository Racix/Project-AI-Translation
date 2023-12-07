import React, { useState, useRef, useEffect } from 'react';

const ChatContainer = ({ messages }) => {
  const containerRef = useRef(null);
  const [scrollToBottom, setScrollToBottom] = useState(true);

  useEffect(() => {
    if (scrollToBottom) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, scrollToBottom]);

  return (
    <div
      ref={containerRef}
      style={{
        height: '40vh', //vh = view height
        width: '80vw', //vw = view width
        border: '1px solid #ccc',
        overflowY: 'auto',
        bottom: '10px',
        left: '10px',
      }}
    >
      {messages.map((message, index) => (
        <div
          key={index}
          style={{
            padding: '8px',
            border: '1px solid #ddd',
            marginBottom: '4px',
            backgroundColor: '#f9f9f9',
          }}
        >
          {message.text}
        </div>
      ))}
    </div>
  );
};

export default ChatContainer;