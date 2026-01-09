"""
Desktop notification module - Windows toast notifications
"""
import threading
from typing import Optional

# Try ctypes approach for Windows notifications
from ctypes import windll, Structure, c_int, byref

# Use tkinter messagebox as simple fallback
import tkinter as tk
from tkinter import messagebox

from ai.signal_model import TradingSignal


def show_notification(
    title: str,
    message: str,
    duration: int = 5000
):
    """
    Show a desktop notification.
    
    Args:
        title: Notification title
        message: Notification body
        duration: How long to show (ms)
    """
    def _show():
        try:
            # Try Windows toast via temporary tkinter window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            root.attributes('-topmost', True)
            
            # Show messagebox (not ideal but works everywhere)
            # For a real toast, you'd use win10toast or similar
            # This is a quick workaround
            root.after(duration, root.destroy)
            
            # Create a small top-right popup instead
            popup = tk.Toplevel(root)
            popup.title("")
            popup.geometry("300x100+{}+50".format(root.winfo_screenwidth() - 320))
            popup.overrideredirect(True)
            popup.attributes('-topmost', True)
            popup.configure(bg='#1a1a2e')
            
            # Title
            tk.Label(
                popup, 
                text=title, 
                font=("Segoe UI", 11, "bold"),
                fg='white',
                bg='#1a1a2e'
            ).pack(pady=(10, 5))
            
            # Message
            tk.Label(
                popup,
                text=message,
                font=("Segoe UI", 10),
                fg='#a0a0a0',
                bg='#1a1a2e',
                wraplength=280
            ).pack(pady=5)
            
            # Auto-close
            popup.after(duration, popup.destroy)
            popup.after(duration + 100, root.destroy)
            
            root.mainloop()
            
        except Exception as e:
            print(f"Notification error: {e}")
    
    threading.Thread(target=_show, daemon=True).start()


def show_signal_notification(signal: TradingSignal):
    """Show notification for a trading signal"""
    if signal.direction == "CALL":
        title = "🟢 CALL Signal"
        color = "#00d26a"
    elif signal.direction == "PUT":
        title = "🔴 PUT Signal"
        color = "#ff4757"
    else:
        title = "⚪ No Trade"
        color = "#a0a0a0"
    
    message = f"{signal.asset}\n⏱️ Expiry: {signal.expiry} | 📊 {signal.confidence}%"
    
    show_notification(title, message, duration=8000)


def show_capture_notification(count: int):
    """Show notification when image is captured"""
    show_notification(
        "📸 Captured",
        f"Screenshot #{count} saved",
        duration=2000
    )


if __name__ == "__main__":
    print("Testing notifications...")
    show_notification("Test Title", "This is a test notification message", 3000)
    
    import time
    time.sleep(5)
    print("Done!")
