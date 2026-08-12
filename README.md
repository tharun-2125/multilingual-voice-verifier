# TraceClaim (Phase 1)

TraceClaim is a web app that detects and traces misinformation in WhatsApp-style voice forwards, specifically designed to handle Tamil-English code-mixed audio. This project is built as an AI/ML engineering portfolio piece.

## Phase 1 Capabilities
- Audio ingestion (upload .ogg, .mp3, .wav).
- Local transcription using `faster-whisper`.
- Persistence of transcriptions in a local SQLite database.
- A minimal React/Tailwind frontend for testing.

> **Note on Language Support**: Whisper attempts to transcribe code-mixed Tamil/English, but it may occasionally struggle or bias towards one language depending on the dominant spoken words.

## Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js & npm

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`.

## Verification / Testing
To test the pipeline end-to-end:
1. Start both the backend and frontend servers as described above.
2. Open `http://localhost:5173` in your browser.
3. Upload a test audio file (e.g., a WhatsApp voice note in `.ogg` format, or a `.wav`/`.mp3` recording of yourself speaking a mix of Tamil and English).
4. Click "Transcribe" and wait for the model to process the audio (processing time depends on your CPU/GPU).
5. The detected language and transcription text will appear on the screen.
