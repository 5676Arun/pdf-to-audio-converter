import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [language, setLanguage] = useState('en');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please select a valid PDF file');
    }
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    setLoading(true);
    setError('');
    setAudioUrl('');

    try {
      const response = await axios.post('/api/convert', formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Create a URL for the audio blob
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
    } catch (err) {
      console.error('Error during conversion:', err);
      if (err.response && err.response.data) {
        // Handle error responses with text
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorData = JSON.parse(reader.result);
            setError(errorData.error || 'Failed to convert PDF to audio');
          } catch (e) {
            setError('Failed to convert PDF to audio');
          }
        };
        reader.readAsText(err.response.data);
      } else {
        setError('Failed to connect to the server');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF to Audio Converter</h1>
        <p>Upload a PDF file and convert it to speech</p>
      </header>
      <main>
        <form onSubmit={handleSubmit}>
          <div className="file-upload">
            <label htmlFor="file-input">
              {file ? file.name : 'Choose a PDF file'}
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
              />
            </label>
          </div>

          <div className="language-select">
            <label htmlFor="language-select">Language:</label>
            <select
              id="language-select"
              value={language}
              onChange={handleLanguageChange}
            >
              <option value="en">English</option>
              <option value="fr">French</option>
              <option value="es">Spanish</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ru">Russian</option>
              <option value="zh-CN">Chinese (Simplified)</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
              <option value="hi">Hindi</option>
            </select>
          </div>

          <button 
            type="submit" 
            className="convert-btn"
            disabled={loading || !file}
          >
            {loading ? 'Converting...' : 'Convert to Audio'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {audioUrl && (
          <div className="audio-player">
            <h3>Your Audio File:</h3>
            <audio controls src={audioUrl}>
              Your browser does not support the audio element.
            </audio>
            <div className="download-link">
              <a href={audioUrl} download="converted-audio.mp3">
                Download Audio File
              </a>
            </div>
          </div>
        )}
      </main>
      <footer>
        <p>PDF to Audio Converter - Cloud Computing Project</p>
      </footer>
    </div>
  );
}

export default App;
