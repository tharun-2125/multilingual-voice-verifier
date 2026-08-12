import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid

from .. import models, schemas
from ..database import get_db
from ..services.transcription import transcribe_gemini, transcribe_whisper, extract_claim_gemini
from ..services.recommendations import classify_content, fetch_recommendations

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a"}

@router.post("/upload-audio", response_model=schemas.Transcription)
async def upload_audio(
    file: UploadFile = File(...), 
    language: str = Form(...),
    source_language: str = Form("auto"),
    pipeline: str = Form("gemini"),
    suggest_links: bool = Form(True),
    extract_claim: bool = Form(True),
    db: Session = Depends(get_db)
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Supported formats: .ogg, .mp3, .wav, .m4a")

    # Generate a unique filename to prevent collisions
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file temporarily
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        # Transcribe and Translate based on selected pipeline
        if pipeline == "gemini":
            result = transcribe_gemini(file_path, target_language=language)
        elif pipeline == "whisper":
            result = transcribe_whisper(file_path, target_language=language, source_language=source_language)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported pipeline: {pipeline}")
        
        # Perform Content Classification & Link Recommendation
        content_category = "other"
        recommendations = []
        translated_meaning = result.get("translated_meaning")
        
        if translated_meaning and suggest_links:
            try:
                classification = classify_content(translated_meaning)
                content_category = classification.get("content_category", "other")
                key_topics = classification.get("key_topics", [])
                recommendations = fetch_recommendations(content_category, key_topics)
            except Exception as e:
                print(f"Warning: Classification or recommendation failed: {e}")
        
        # Extract claim if enabled
        extracted_claim = None
        if translated_meaning and extract_claim:
            try:
                extracted_claim = extract_claim_gemini(translated_meaning)
            except Exception as e:
                print(f"Warning: Claim extraction failed: {e}")
        
        # Save to database
        db_transcription = models.Transcription(
            filename=file.filename,
            original_meaning=result["original_meaning"],
            translated_meaning=result["translated_meaning"],
            translated_main=result.get("translated_main"),
            target_language=result["target_language"],
            detected_language=result["detected_language"],
            pipeline=pipeline,
            content_category=content_category,
            recommendations=recommendations,
            extracted_claim=extracted_claim
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        
        return db_transcription

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

