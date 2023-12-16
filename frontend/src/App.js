import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import './styles/App.css';
import logo from './img/Doris_logo.png'
import TranscriptionDisplay from './TranscriptionDisplay';
import Upload from './Upload';
import LiveTranscription from './LiveTranscription';

function Navbar() {
  return (
    <nav className="navbar">
      <img src={logo} alt="Logo" className="navbar-logo" />
      <Link to="/" className="nav-item">Home</Link>
      <Link to="/upload" className="nav-item">Upload & Process</Link>
      <Link to="/live" className="nav-item">Live Transcription</Link>
    </nav>
  );
}

function App() {
  
  return (
    <Router>
      <div className="App">
        <Navbar /> 
        <Routes>
          <Route path="/" element={
            <>
            <h1>Welcome to DoRiS</h1>
            <div className='dorisField'>A tool for transcribing and diarizing your recordings</div>
            <div className='app-body'>
            <div className='textField'>
              Today, there is a pressing need for speech transcription and translation to increase the accessibility of information for everyone in society.
              This need comes in various forms such as live meetings, recorded videos, or phone calls. Therefore, we are developing a service that, with the help of AI,
              can automate these processes to efficiently use time and resources.
            </div>
            <div className='textField'>
              We are a group of 8 students from Luleå University of Technology in Sweden that has developed this work during a project course on the Master Programme in Computer
              Science and Engineering, with specialisation in Information and Communication Technology. Our work combines some more or less well-known AI tools for Transcription,
              Diarization, Translation, and text summarization.
            </div>
            <div className='textField'> 
              <strong>Models Used:</strong>
              <ul>
                <li><a href="https://github.com/openai/whisper">Whisper</a>: Handles transcription.</li>
                <li><a href="https://github.com/NVIDIA/NeMo">NeMo</a>: Handles diarization.</li>
                <li><a href="https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF">Mistral7b OpenHermes 2.5</a> with <a href="https://github.com/run-llama/llama_index">LLama-index</a>: Utilized for summarization, requires GPU.</li>
                <li><a href="https://github.com/argosopentech/argos-translate">Argos-translate</a>: Provides translation functionality.</li>
              </ul>
            </div>
            <div className='textField'>
              <strong>Usage:</strong>
              <br></br>
              Navigate to Upload & processes to get your files analysed and view the content.  

              <br></br>
              <br></br>
              To start live transcription, one in the call must run the recorder on their own mahcine. To do this, navigate to the sound_driver directory and run the sound_driver.exe file. When this is done connect to the channel in the Live transcription page here on the website and connect to the channel.
              <br></br>
              <br></br>
              <a href='https://github.com/Racix/Project-AI-Translation/tree/main'> Read more in the github repository</a>
            </div>
            </div>
          </>
        } />
          
          <Route path="/display/:id" element={<TranscriptionDisplay />} />
          <Route path="/upload" element={<Upload />}/>
          <Route path="/live" element={<LiveTranscription />}/>

        </Routes>
      </div>
    </Router>
  );
}

export default App;