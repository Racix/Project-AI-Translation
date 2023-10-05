import React, { useState } from 'react';
import './Upload.css';

function Upload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('No file chosen');

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
      här ska in en lista på alla uppladdade filer som ska kunna proceseras
    </div>
  );
}

export default Upload;