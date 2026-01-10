"""
AI Trading Analyst
==================

A lightweight Python application that captures chart screenshots
and uses AI vision to provide binary trading signals.

Usage:
    python main.py

Hotkeys:
    - 'aa' (double-a): Capture current window
    - 'c': Complete capture and analyze
    - 'x': Cancel/clear captured images
    - 'v': View cache folder
    - 'q': Quit application
"""

import sys
import time
import threading
from datetime import datetime
import subprocess
import os
import ctypes
from pathlib import Path

# Fix blurry UI on Windows high-DPI displays (must be before tkinter import)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import COLORS, CACHE_DIR
from capture.hotkey_listener import HotkeyListener
from capture.screenshot import capture_active_window, get_active_window_title
from capture.image_cache import cache, cleanup_old_cache_files
from ai.analyzer_factory import analyze_charts, test_providers
from notify.sound_alert import play_capture_sound, play_signal_sound, play_error_sound
from notify.overlay import show_signal_overlay

# Dashboard instead of tkinter sidebar
from dashboard.app import run_dashboard, emit_status, emit_captures, emit_signal, emit_error, emit_providers
from notify.desktop_notification import show_notification


class TradingAnalyst:
    """
    Main application controller.
    Coordinates capture, analysis, and display.
    """
    
    def __init__(self):
        self._running = False
        self._analyzing = False
        
        # Initialize hotkey listener with callbacks
        self._hotkey_listener = HotkeyListener(
            on_capture=self._on_capture,
            on_complete=self._on_complete,
            on_cancel=self._on_cancel,
            on_view=self._on_view,
            on_quit=self._on_quit
        )
    
    def start(self):
        """Start the application"""
        print("\n" + "=" * 50)
        print("🤖 AI Trading Analyst")
        print("=" * 50)
        
        # Clean up old cache files
        cleanup_old_cache_files()
        
        # Test AI providers
        print()
        available = test_providers()
        
        if not available:
            print("\n⚠️  No AI providers configured!")
            print("Please copy .env.example to .env and add your API key(s)")
            print("Get a free Gemini key: https://aistudio.google.com/apikey")
            return
        
        print()
        
        # Start web dashboard
        run_dashboard(open_browser=True)
        time.sleep(1.5)  # Let dashboard initialize
        
        # Emit initial providers
        emit_providers(available)
        
        # Start hotkey listener
        self._running = True
        self._hotkey_listener.start()
        
        emit_status("Ready")
        
        print("\n✅ Application started!")
        print("   Position this window and the sidebar beside your Quotex browser")
        print("   Then start capturing charts with 'aa' hotkey")
        print("\n   Press 'q' to quit\n")
        
        # Main loop
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._on_quit()
    
    def _on_capture(self):
        """Handle capture hotkey (double-a)"""
        if self._analyzing:
            print("⚠️ Analysis in progress, please wait...")
            return
        
        emit_status("Capturing...")
        
        # Capture screenshot
        window_title = get_active_window_title()
        image_path = capture_active_window()
        
        if image_path:
            # Add to cache
            if cache.add(image_path, window_title):
                play_capture_sound()
                # Update dashboard
                emit_captures([{'path': str(img.path)} for img in cache.images])
                emit_status(f"Captured #{cache.count}")
        else:
            print("❌ Capture failed")
            emit_status("Capture failed")
            play_error_sound()
    
    def _on_complete(self):
        """Handle complete hotkey (c) - trigger analysis"""
        if self._analyzing:
            print("⚠️ Analysis already in progress...")
            return
        
        if cache.count == 0:
            print("⚠️ No images to analyze. Capture some charts first with 'aa'")
            emit_status("No images")
            return
        
        # Run analysis in background thread
        threading.Thread(target=self._run_analysis, daemon=True).start()
    
    def _run_analysis(self):
        """Run AI analysis on cached images"""
        self._analyzing = True
        
        try:
            print(f"\n🔍 Analyzing {cache.count} image(s)...")
            emit_status("Analyzing...")
            
            # Get image paths
            image_paths = cache.image_paths
            
            # Run analysis
            result = analyze_charts(image_paths)
            
            if result.success:
                signal = result.signal
                print(f"\n📊 Signal: {signal.direction}")
                print(f"   Asset: {signal.asset}")
                print(f"   Confidence: {signal.confidence}%")
                print(f"   Expiry: {signal.expiry}")
                print(f"   Timing: {signal.entry_timing}")
                print(f"   Reason: {signal.reasoning}")
                
                # Update dashboard
                signal_data = {
                    'direction': signal.direction,
                    'asset': signal.asset,
                    'confidence': signal.confidence,
                    'expiry': signal.expiry,
                    'entry_timing': signal.entry_timing,
                    'reasoning': signal.reasoning,
                    'patterns_detected': signal.patterns_detected,
                    'key_levels': signal.key_levels,
                    'provider': result.provider_used,
                    'analysis_time_ms': result.analysis_time_ms
                }
                
                # Pass chart paths for database storage
                chart_paths = [str(p) for p in image_paths]
                emit_signal(signal_data, chart_paths)
                
                # Show desktop notification
                show_notification(signal, auto_dismiss=20)
                
                status = f"{signal.direction} {signal.confidence}%"
                emit_status(status)
            else:
                print(f"\n❌ Analysis failed: {result.error}")
                print(f"   📂 Images kept in: {CACHE_DIR}")
                print(f"   Press 'v' to view captured images")
                emit_error(result.error or "Unknown error")
                emit_status("Error - images kept")
                play_error_sound()
                return  # Keep images on error!
            
            # Clear cache files only after SUCCESSFUL analysis
            # But DON'T clear the thumbnail display - keep it visible
            cache.clear(delete_files=True)
            # Keep thumbnails visible in dashboard
            
        except Exception as e:
            print(f"\n❌ Analysis error: {e}")
            print(f"   📂 Images kept in: {CACHE_DIR}")
            emit_error(str(e))
            emit_status("Error - images kept")
            play_error_sound()
        
        finally:
            self._analyzing = False
    
    def _on_cancel(self):
        """Handle cancel hotkey (x) - clear cached images"""
        count = cache.clear(delete_files=True)
        emit_captures([])
        emit_status("Cleared")
        print(f"🗑️ Cleared {count} image(s)")
    
    def _on_view(self):
        """Handle view hotkey (v) - open cache folder"""
        print(f"📂 Opening cache folder: {CACHE_DIR}")
        try:
            os.startfile(str(CACHE_DIR))
        except Exception as e:
            print(f"Could not open folder: {e}")
            # Fallback: print the path
            print(f"   Manually open: {CACHE_DIR}")
    
    def _on_quit(self):
        """Handle quit hotkey (q)"""
        print("\n👋 Shutting down...")
        self._running = False
        
        # Clean up
        cache.clear(delete_files=True)
        self._hotkey_listener.stop()
        # Dashboard runs in background thread, will close with app
        
        print("Goodbye!")


def main():
    """Application entry point"""
    app = TradingAnalyst()
    app.start()


if __name__ == "__main__":
    main()
