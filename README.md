# TraceClaim 🎙️🔍

> **AI-powered misinformation detection for voice forwards** — transcribes, translates, classifies, and fact-checks WhatsApp-style audio clips with support for Tamil-English code-mixed speech.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Audio Transcription** | Upload `.ogg`, `.mp3`, `.wav`, `.m4a` files and get instant transcriptions |
| 🌐 **Multi-pipeline Support** | Choose between **Gemini AI** (cloud) or **Whisper** (local/offline) |
| 🔁 **Translation** | Translate transcriptions into any target language |
| 🏷️ **Content Classification** | Automatically categorizes content (news, health, politics, etc.) |
| 🔗 **Smart Link Recommendations** | Suggests relevant fact-check and reference links based on content topics |
| 🧠 **Claim Extraction** | Extracts the core verifiable claim from the audio using Gemini AI |
| 🗄️ **Persistent Storage** | All results saved to a local SQLite database |
| 🇮🇳 **Tamil-English Code-Mix** | Designed specifically for Indian regional language audio |

---

## 🏗️ Architecture

```
project-deva/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── routes/           # API route handlers
│   │   ├── services/         # Core logic (transcription, recommendations)
│   │   ├── models.py         # SQLAlchemy DB models
│   │   ├── schemas.py        # Pydantic response schemas
│   │   └── database.py       # DB engine & session
│   ├── main.py               # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # React + Vite frontend
    ├── src/
    │   ├── App.jsx           # Main UI component
    │   └── api.js            # Backend API calls
    ├── package.json
    └── vite.config.js
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Local speech-to-text (CTranslate2-based)
- [Google Gemini AI](https://ai.google.dev/) — Cloud transcription, translation & claim extraction
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM with SQLite
- [GNews API](https://gnews.io/) + [SerpAPI](https://serpapi.com/) — Link recommendations

**Frontend**
- [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 🚀 Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

---

### 1. Clone the repo

```bash
git clone https://github.com/tharun-2125/traceclaim.git
cd traceclaim
```

---

### 2. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and fill in your API keys (see below)

# Start the backend server
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**
Interactive API docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in your keys:

```env
# Google Gemini API Key — https://aistudio.google.com/app/apikey
GEMINI_API_KEY=

# GNews API Key — https://gnews.io/
GNEWS_API_KEY=

# SerpAPI Key — https://serpapi.com/
SERPAPI_KEY=
```

> **Note:** The Whisper pipeline works fully offline without any API keys. Only Gemini-based features require `GEMINI_API_KEY`.

---

## 📡 API Reference

### `POST /api/upload-audio`

Upload an audio file for processing.

| Field | Type | Description |
|---|---|---|
| `file` | File | Audio file (`.ogg`, `.mp3`, `.wav`, `.m4a`) |
| `language` | string | Target translation language (e.g. `"english"`) |
| `source_language` | string | Source language hint (default: `"auto"`) |
| `pipeline` | string | `"gemini"` or `"whisper"` (default: `"gemini"`) |
| `suggest_links` | bool | Whether to fetch link recommendations (default: `true`) |
| `extract_claim` | bool | Whether to extract the core claim (default: `true`) |

**Example Response:**
```json
{
  "id": 1,
  "filename": "voice_note.ogg",
  "original_meaning": "...",
  "translated_meaning": "...",
  "detected_language": "Tamil",
  "target_language": "english",
  "pipeline": "gemini",
  "content_category": "health",
  "extracted_claim": "Drinking hot water cures COVID-19",
  "recommendations": ["https://..."],
  "created_at": "2026-08-12T06:00:00"
}
```

---

## 📝 Language Support Note

Whisper handles Tamil-English code-mixed audio but may occasionally bias towards one language depending on dominant spoken words. The **Gemini pipeline** generally handles code-switching more gracefully.

---

## 👥 Authors

**Tharun Natarajan** — [tharunnatarajan2125@gmail.com](mailto:tharunnatarajan2125@gmail.com)

**Devendran** — [ddeve572@gmail.com](mailto:ddeve572@gmail.com)

Built as an AI/ML engineering portfolio project.
