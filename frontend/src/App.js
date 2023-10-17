import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import TranscriptionDisplay from './TranscriptionDisplay';
import Upload from './Upload'
import './styles/App.css';
import logo from './img/Doris_logo.png'


function Navbar() {
  return (
    <nav className="navbar">
      <img src={logo} alt="Logo" className="navbar-logo" />
      <Link to="/" className="nav-item">Home</Link>
      <Link to="/upload" className="nav-item">Upload & Process</Link>
      <Link to="/display" className="nav-item">Transcription Display</Link>
    </nav>
  );
}


function App() {
  return (
    <Router>
      <div className="App">
        <Navbar /> {/* Navbar added here will be on top */}
        <Routes>
          <Route path="/" element={
            <>
              <h1>Welcome to DoRiS</h1>
              <div>DoRiS is a tool for transcribing and Diarizing your recordings</div>
              <img src={logo} alt="Logo" className="home-page-logo" />
            </>
          } />
          <Route path="/display" element={<TranscriptionDisplay />} />
          <Route path="/upload" element={<Upload />}/>

        </Routes>
      </div>
    </Router>
  );
}


export default App;
