# PDF to Audio Converter

A web application that converts PDF files to audio using text-to-speech technology.

## Features

- Upload PDF files
- Extract text from PDF documents
- Convert text to speech using Google's Text-to-Speech service
- Download the generated audio file
- Parallel processing for faster conversion

## Technology Stack

- **Frontend**: React.js, Bootstrap
- **Backend**: Flask (Python)
- **Containerization**: Docker, Docker Compose
- **Text Extraction**: PyPDF2
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Audio Processing**: pydub

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone this repository:
   ```
   git clone https://github.com/5676Arun/pdf-to-audio-converter.git
   cd pdf-to-audio-converter
   ```

2. Start the application:
   ```
   docker-compose up -d
   ```

3. Access the application:
   - Open your browser and navigate to `http://localhost:3000`

4. Stop the application:
   ```
   docker-compose down
   ```

## Usage

1. Access the web interface
2. Upload a PDF file
3. Click "Convert to Audio"
4. Wait for the conversion to complete
5. Download the audio file

## Viewing Logs

```
# View all logs
docker-compose logs

# View frontend logs
docker-compose logs frontend

# View backend logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f
```

## Development

To make changes to the application:

1. Modify the code
2. Rebuild and restart the containers:
   ```
   docker-compose up -d --build
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 