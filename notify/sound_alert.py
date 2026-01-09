"""
Sound alert module - plays audio notifications
"""
import threading
from pathlib import Path
import os

# Try to import playsound
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

# Alternative: use winsound for Windows
import winsound

from config import ENABLE_SOUNDS, CAPTURE_SOUND, CALL_SOUND, PUT_SOUND, ASSETS_DIR


def _play_beep(frequency: int = 800, duration: int = 150):
    """Play a simple beep using Windows API"""
    try:
        winsound.Beep(frequency, duration)
    except:
        pass


def _play_file(path: Path):
    """Play an audio file"""
    if not path.exists():
        # Fallback to beep
        _play_beep()
        return
    
    if PLAYSOUND_AVAILABLE:
        try:
            playsound(str(path), block=False)
        except:
            _play_beep()
    else:
        _play_beep()


def play_capture_sound():
    """Play sound when screenshot is captured"""
    if not ENABLE_SOUNDS:
        return
    
    def _play():
        if CAPTURE_SOUND.exists():
            _play_file(CAPTURE_SOUND)
        else:
            # Short high beep
            _play_beep(1000, 100)
    
    threading.Thread(target=_play, daemon=True).start()


def play_call_sound():
    """Play sound for CALL signal"""
    if not ENABLE_SOUNDS:
        return
    
    def _play():
        if CALL_SOUND.exists():
            _play_file(CALL_SOUND)
        else:
            # Ascending tone
            _play_beep(600, 100)
            _play_beep(800, 100)
            _play_beep(1000, 150)
    
    threading.Thread(target=_play, daemon=True).start()


def play_put_sound():
    """Play sound for PUT signal"""
    if not ENABLE_SOUNDS:
        return
    
    def _play():
        if PUT_SOUND.exists():
            _play_file(PUT_SOUND)
        else:
            # Descending tone
            _play_beep(1000, 100)
            _play_beep(800, 100)
            _play_beep(600, 150)
    
    threading.Thread(target=_play, daemon=True).start()


def play_signal_sound(direction: str):
    """Play appropriate sound for signal direction"""
    if direction == "CALL":
        play_call_sound()
    elif direction == "PUT":
        play_put_sound()
    else:
        _play_beep(500, 200)  # Neutral beep for no trade


def play_error_sound():
    """Play error sound"""
    if not ENABLE_SOUNDS:
        return
    
    def _play():
        _play_beep(300, 300)
    
    threading.Thread(target=_play, daemon=True).start()


if __name__ == "__main__":
    print("Testing sounds...")
    print("1. Capture sound")
    play_capture_sound()
    import time
    time.sleep(1)
    
    print("2. Call sound")
    play_call_sound()
    time.sleep(1)
    
    print("3. Put sound")
    play_put_sound()
    time.sleep(1)
    
    print("Done!")
