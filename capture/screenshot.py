"""
Screenshot capture module - captures active window
"""
import mss
import mss.tools
from PIL import Image
from pathlib import Path
from datetime import datetime
import win32gui
import win32con
import win32ui
import ctypes
from ctypes import windll

from config import CACHE_DIR


def get_active_window_rect():
    """Get the bounding rectangle of the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hwnd)
        return {
            "left": rect[0],
            "top": rect[1],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1]
        }
    except Exception as e:
        print(f"Error getting active window: {e}")
        return None


def get_active_window_title():
    """Get the title of the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return "Unknown"


def capture_active_window() -> Path | None:
    """
    Capture a screenshot of the currently active window.
    Returns the path to the saved image, or None on failure.
    """
    try:
        # Get active window bounds
        rect = get_active_window_rect()
        if not rect:
            print("Could not get active window rectangle")
            return None
        
        # Ensure valid dimensions
        if rect["width"] <= 0 or rect["height"] <= 0:
            print("Invalid window dimensions")
            return None
        
        # Capture using mss
        with mss.mss() as sct:
            # Capture the region
            screenshot = sct.grab(rect)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"capture_{timestamp}.png"
            filepath = CACHE_DIR / filename
            
            # Save image
            img.save(str(filepath), "PNG")
            
            print(f"📸 Captured: {filepath.name}")
            return filepath
            
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


def capture_full_screen() -> Path | None:
    """
    Capture a screenshot of the entire primary screen.
    Fallback if active window capture fails.
    """
    try:
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"fullscreen_{timestamp}.png"
            filepath = CACHE_DIR / filename
            
            img.save(str(filepath), "PNG")
            
            print(f"📸 Full screen captured: {filepath.name}")
            return filepath
            
    except Exception as e:
        print(f"Full screen capture error: {e}")
        return None


if __name__ == "__main__":
    # Test capture
    print("Testing active window capture...")
    print(f"Active window: {get_active_window_title()}")
    path = capture_active_window()
    if path:
        print(f"Saved to: {path}")
    else:
        print("Capture failed, trying full screen...")
        path = capture_full_screen()
        if path:
            print(f"Full screen saved to: {path}")
