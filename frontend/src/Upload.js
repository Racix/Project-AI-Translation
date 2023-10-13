import React, { useState, useEffect } from 'react';
import './Upload.css';

function Upload() {
  const [file, setFile] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [fileName, setFileName] = useState('No file chosen');

  useEffect(() => {
    const fetchFileList = async () => {
      try {
        const response = await fetch('http://localhost:8080/media');
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

  const processFile = async (mediaId) => {
    try {
      const formData = new FormData();
      const response = await fetch(`http://localhost:8080/media/${mediaId}/analysis`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        alert(data.message);
      } else {
        alert('Error uploading file!');
      }
    } catch (error) {
      console.error('Error fetching file content.', error);
    }
  };

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
    setFileName(event.target.files[0] ? event.target.files[0].name : 'No file chosen');
  };

  const onUpload = async () => {
    if (!file) return;
  
    const formData = new FormData();
    formData.append('file', file);
  
    try {
      const response = await fetch('http://localhost:8080/media', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        alert('File uploaded successfully!');
        window.location.reload();  // Reload the entire page
      } else {
        alert('Error uploading file!');
      }
    } catch (error) {
      console.error('There was an error uploading the file.', error);
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
        <label 
          htmlFor="fileInput" 
          className="file-label"
        >
          Browse
        </label>
        <span style={{ marginLeft: '10px' }}>{fileName}</span>
      </div>
      <button 
        onClick={onUpload} 
        className="upload-button"
      >
        Upload
      </button>
      <ul className="file-list">
        {fileList.map(file => (
          <li key={file._id}>
            {file.name}
            <button onClick={() => processFile(file._id)} className="analyze-button">
              Analyze
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Upload;
