import os
import tempfile
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
from gtts import gTTS
import concurrent.futures
import math
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
ALLOWED_EXTENSIONS = {'pdf'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    logger.debug(f"Extracting text from PDF: {pdf_path}")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text if page_text else ""
                logger.debug(f"Extracted {len(page_text) if page_text else 0} characters from page {page_num+1}")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise
    return text

def process_text_chunk(chunk_data):
    chunk_text, chunk_idx, temp_dir, language = chunk_data
    logger.debug(f"Processing chunk {chunk_idx} with {len(chunk_text)} characters")
    
    # Skip empty chunks
    if not chunk_text.strip():
        return None
    
    # Generate temporary file path for this chunk
    temp_file = os.path.join(temp_dir, f"chunk_{chunk_idx}.mp3")
    
    # Convert chunk to speech
    tts = gTTS(text=chunk_text, lang=language, slow=False)
    tts.save(temp_file)
    
    logger.debug(f"Saved chunk {chunk_idx} to {temp_file}")
    return temp_file

def text_to_speech(text, output_path, language='en'):
    logger.debug(f"Converting {len(text)} characters to speech in language: {language}")
    
    # Create temporary directory for chunks
    with tempfile.TemporaryDirectory() as temp_dir:
        # Split text into chunks of roughly 2000 characters each
        # Don't split in the middle of words
        chunk_size = 2000
        chunks = []
        current_chunk = ""
        
        words = text.split()
        for word in words:
            if len(current_chunk) + len(word) + 1 > chunk_size:
                chunks.append(current_chunk)
                current_chunk = word + " "
            else:
                current_chunk += word + " "
        
        if current_chunk:
            chunks.append(current_chunk)
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        
        # Process chunks in parallel
        chunk_data = [(chunk, idx, temp_dir, language) for idx, chunk in enumerate(chunks)]
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            chunk_files = list(executor.map(process_text_chunk, chunk_data))
        
        # Filter out None results (empty chunks)
        chunk_files = [f for f in chunk_files if f]
        
        if not chunk_files:
            raise ValueError("No audio could be generated from the text")
        
        # If only one chunk, just rename it
        if len(chunk_files) == 1:
            logger.debug(f"Only one chunk, renaming {chunk_files[0]} to {output_path}")
            os.rename(chunk_files[0], output_path)
        else:
            # Combine all audio chunks
            logger.debug(f"Combining {len(chunk_files)} audio chunks")
            combined = AudioSegment.empty()
            for chunk_file in chunk_files:
                audio_chunk = AudioSegment.from_mp3(chunk_file)
                combined += audio_chunk
            
            # Export combined audio
            logger.debug(f"Exporting combined audio to {output_path}")
            combined.export(output_path, format="mp3")
            
    logger.debug(f"Audio saved to: {output_path}")
    return output_path

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/convert', methods=['POST'])
def convert_pdf_to_audio():
    logger.debug("Convert API called")
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        # Save the uploaded PDF
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.debug(f"Saving uploaded file to: {pdf_path}")
        file.save(pdf_path)
        
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                logger.error("No text could be extracted from the PDF")
                return jsonify({"error": "No text could be extracted from the PDF"}), 400
            
            # Convert text to speech
            language = request.form.get('language', 'en')
            logger.debug(f"Using language: {language}")
            audio_filename = f"{os.path.splitext(filename)[0]}.mp3"
            audio_path = os.path.join(app.config['OUTPUT_FOLDER'], audio_filename)
            
            text_to_speech(text, audio_path, language)
            
            # Return the audio file
            logger.debug(f"Sending audio file: {audio_path}")
            return send_file(
                audio_path,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name=audio_filename
            )
        
        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    return jsonify({"error": "File type not allowed. Only PDF files are accepted."}), 400

if __name__ == '__main__':
    logger.info("Starting Flask server")
    app.run(host='0.0.0.0', port=5000, debug=True) 