"""
Global hotkey listener - detects double-press patterns
"""
import time
import threading
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from config import (
    CAPTURE_KEY, 
    COMPLETE_KEY, 
    CANCEL_KEY, 
    QUIT_KEY,
    DOUBLE_PRESS_TIMEOUT
)

VIEW_KEY = 'v'  # View cache folder


class HotkeyListener:
    """
    Listens for global hotkeys with double-press detection.
    
    Hotkeys:
    - Double 'a': Trigger capture
    - 'c': Complete/analyze
    - 'x': Cancel/clear
    - 'v': View cache folder
    - 'q': Quit
    """
    
    def __init__(
        self,
        on_capture: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        on_view: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        self.on_capture = on_capture or (lambda: print("Capture triggered"))
        self.on_complete = on_complete or (lambda: print("Complete triggered"))
        self.on_cancel = on_cancel or (lambda: print("Cancel triggered"))
        self.on_view = on_view or (lambda: print("View triggered"))
        self.on_quit = on_quit or (lambda: print("Quit triggered"))
        
        self._last_a_time = 0
        self._listener: Optional[keyboard.Listener] = None
        self._running = False
        self._lock = threading.Lock()
        
    def _on_press(self, key):
        """Handle key press events"""
        try:
            # Get the character if it's a regular key
            if isinstance(key, KeyCode):
                char = key.char.lower() if key.char else ""
            else:
                return  # Ignore special keys
            
            current_time = time.time()
            
            # Check for double-'a' press
            if char == CAPTURE_KEY:
                with self._lock:
                    time_diff = current_time - self._last_a_time
                    self._last_a_time = current_time
                    
                    if time_diff <= DOUBLE_PRESS_TIMEOUT:
                        # Double press detected!
                        self._last_a_time = 0  # Reset to prevent triple-trigger
                        threading.Thread(target=self.on_capture, daemon=True).start()
                        
            elif char == COMPLETE_KEY:
                threading.Thread(target=self.on_complete, daemon=True).start()
                
            elif char == CANCEL_KEY:
                threading.Thread(target=self.on_cancel, daemon=True).start()
            
            elif char == VIEW_KEY:
                threading.Thread(target=self.on_view, daemon=True).start()
                
            elif char == QUIT_KEY:
                self.on_quit()
                
        except Exception as e:
            print(f"Hotkey error: {e}")
    
    def start(self):
        """Start listening for hotkeys"""
        if self._running:
            return
            
        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        print("🎹 Hotkey listener started")
        print(f"   • Double '{CAPTURE_KEY}' to capture")
        print(f"   • '{COMPLETE_KEY}' to analyze")
        print(f"   • '{CANCEL_KEY}' to cancel")
        print(f"   • '{VIEW_KEY}' to view images")
        print(f"   • '{QUIT_KEY}' to quit")
        
    def stop(self):
        """Stop listening for hotkeys"""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        print("🎹 Hotkey listener stopped")
        
    def is_running(self) -> bool:
        """Check if listener is active"""
        return self._running


if __name__ == "__main__":
    # Test hotkey listener
    print("Testing hotkey listener...")
    print("Press 'aa' (double-a) to test capture")
    print("Press 'c' to test complete")
    print("Press 'q' to quit")
    
    def test_capture():
        print("✅ CAPTURE TRIGGERED!")
        
    def test_complete():
        print("✅ COMPLETE TRIGGERED!")
        
    def test_quit():
        print("✅ QUIT - Stopping...")
        listener.stop()
    
    listener = HotkeyListener(
        on_capture=test_capture,
        on_complete=test_complete,
        on_quit=test_quit
    )
    
    listener.start()
    
    # Keep running until stopped
    try:
        while listener.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        listener.stop()
