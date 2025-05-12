from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .api.voice_routes import router as voice_router

# Create FastAPI application
app = FastAPI(title="Voice AI Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(voice_router, prefix="/api/voice", tags=["voice"])

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """
    Serve the main web interface
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}

@app.get("/test")
async def get_test_page():
    """
    Serve the API test page
    """
    html_content = open("app/static/test.html", "r").read()
    return HTMLResponse(content=html_content)