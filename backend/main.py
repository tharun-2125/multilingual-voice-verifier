import sys
# Ensure stdout and stderr use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine

from app.routes import upload

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TraceClaim API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:8080",
        # Production — Vercel (update this after your first Vercel deploy)
        "https://traceclaim.vercel.app",
        # Allow all Vercel preview deployments for this project
        "https://traceclaim-*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Audio Upload"])

@app.get("/")
def read_root():
    return {"message": "Welcome to TraceClaim API"}
