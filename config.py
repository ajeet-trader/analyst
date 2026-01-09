"""
Configuration settings for AI Trading Analyst
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === Paths ===
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
CACHE_DIR = BASE_DIR / "cache"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# === API Keys ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")  # Free tier
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")   # Free tier

# === AI Provider Enable/Disable ===
ENABLE_GROQ = True          # FREE - Primary
ENABLE_HUGGINGFACE = True   # FREE - Secondary
ENABLE_TOGETHER = True      # FREE tier - Tertiary
ENABLE_GEMINI = False       # Freemium - Disabled by default
ENABLE_OPENAI = False       # Paid - Disabled by default

# === Hotkey Settings ===
CAPTURE_KEY = 'a'                    # Press twice to capture
COMPLETE_KEY = 'c'                   # Complete and analyze
CANCEL_KEY = 'x'                     # Cancel/clear captures
QUIT_KEY = 'q'                       # Quit application
DOUBLE_PRESS_TIMEOUT = 0.4           # Seconds between double-press

# === Capture Settings ===
MAX_CACHED_IMAGES = 10               # Maximum images to cache
CAPTURE_DELAY_MS = 100               # Delay after capture for stability

# === AI Settings ===
AI_TIMEOUT_SECONDS = 30              # Max wait for AI response
AI_MAX_RETRIES = 2                   # Retries before fallback
MIN_CONFIDENCE_THRESHOLD = 60        # Minimum confidence to show signal

# === Signal Settings ===
SIGNAL_DISPLAY_DURATION = 15         # Seconds to show signal overlay
CAPTURE_TO_SIGNAL_BUFFER = 15        # Seconds to account for delay

# === UI Settings ===
OVERLAY_POSITION = "bottom-right"    # Corner position for overlay
SIDEBAR_WIDTH = 320                  # Left sidebar panel width
SIDEBAR_OPACITY = 0.95               # Sidebar transparency

# === Sound Settings ===
ENABLE_SOUNDS = True
CAPTURE_SOUND = ASSETS_DIR / "capture.wav"
CALL_SOUND = ASSETS_DIR / "call.wav"
PUT_SOUND = ASSETS_DIR / "put.wav"

# === Colors ===
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_panel": "#16213e",
    "accent_green": "#00d26a",
    "accent_red": "#ff4757",
    "accent_blue": "#4dabf7",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#2d3748",
}
