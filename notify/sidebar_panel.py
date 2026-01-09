"""
Modern Glassmorphism Floating Card UI
=====================================
Beautiful floating panel with:
- Signal display with confidence ring
- Countdown timer
- Chart thumbnails
- Detailed reasoning (WHY to trade)
- Pattern badges
- Win/Loss tracking
"""
import customtkinter as ctk
from tkinter import Canvas
import threading
from typing import Optional, List
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import os
import ctypes
import math
import csv
from pathlib import Path

# Fix DPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

from config import CACHE_DIR
from ai.signal_model import TradingSignal, AnalysisResult
from capture.image_cache import CachedImage

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernTradingPanel:
    """
    Floating glassmorphism card with all trading info.
    """
    
    def __init__(self):
        self._root: Optional[ctk.CTk] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # State
        self._cached_images: List[CachedImage] = []
        self._current_signal: Optional[TradingSignal] = None
        self._current_result: Optional[AnalysisResult] = None
        self._timer_seconds = 0
        self._timer_running = False
        
        # Stats
        self._wins = 0
        self._losses = 0
        self._total_signals = 0
        
        # Colors - Modern purple-blue gradient theme
        self.colors = {
            "bg_gradient_start": "#1a1a2e",
            "bg_gradient_end": "#16213e",
            "card_bg": "#1f2937",
            "card_border": "#374151",
            "glass_bg": "#ffffff10",
            "text_white": "#ffffff",
            "text_gray": "#9ca3af",
            "text_dim": "#6b7280",
            "accent_green": "#10b981",
            "accent_green_glow": "#10b98140",
            "accent_red": "#ef4444",
            "accent_red_glow": "#ef444440",
            "accent_blue": "#3b82f6",
            "accent_purple": "#8b5cf6",
            "accent_yellow": "#f59e0b",
        }
        
        # UI refs
        self._signal_label = None
        self._asset_label = None
        self._expiry_label = None  # NEW: Explicit expiry display
        self._confidence_canvas = None
        self._confidence_label = None
        self._timer_label = None
        self._reasoning_text = None
        self._patterns_frame = None
        self._thumbnails_frame = None
        self._stats_label = None
        self._photo_refs = []
        self._saved_thumbnails = []  # Keep thumbnails after analysis
        
        # Log file
        self._log_path = Path(CACHE_DIR).parent / "signal_log.csv"
        self._init_log()
    
    def _init_log(self):
        """Initialize signal log file"""
        if not self._log_path.exists():
            with open(self._log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'asset', 'direction', 'confidence', 
                    'expiry', 'patterns', 'reasoning', 'result'
                ])
    
    def start(self):
        """Start the panel"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._create_window, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the panel"""
        self._running = False
        self._timer_running = False
        if self._root:
            try:
                self._root.quit()
                self._root.destroy()
            except:
                pass
            self._root = None
    
    def _create_window(self):
        """Create the modern floating card"""
        self._root = ctk.CTk()
        self._root.title("Quotex AI")
        
        # Window setup - floating square
        width, height = 480, 580
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2 - 50
        
        self._root.geometry(f"{width}x{height}+{x}+{y}")
        self._root.configure(fg_color=self.colors["bg_gradient_start"])
        self._root.attributes('-topmost', True)
        self._root.resizable(False, False)
        
        # Make it draggable
        self._root.bind('<Button-1>', self._start_drag)
        self._root.bind('<B1-Motion>', self._do_drag)
        self._drag_x = 0
        self._drag_y = 0
        
        # Main container with padding
        main = ctk.CTkFrame(self._root, fg_color="transparent")
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === HEADER ===
        header = ctk.CTkFrame(main, fg_color="transparent", height=40)
        header.pack(fill='x', pady=(0, 15))
        
        # Logo
        ctk.CTkLabel(
            header,
            text="⚡ QUOTEX AI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["accent_blue"]
        ).pack(side='left')
        
        # Status
        self._status_label = ctk.CTkLabel(
            header,
            text="● Ready",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["accent_green"]
        )
        self._status_label.pack(side='right')
        
        # === SIGNAL CARD ===
        signal_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        signal_card.pack(fill='x', pady=(0, 15))
        
        # Signal row
        signal_row = ctk.CTkFrame(signal_card, fg_color="transparent")
        signal_row.pack(fill='x', padx=20, pady=15)
        
        # Left: Signal direction
        signal_left = ctk.CTkFrame(signal_row, fg_color="transparent")
        signal_left.pack(side='left')
        
        self._signal_label = ctk.CTkLabel(
            signal_left,
            text="WAITING",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_gray"]
        )
        self._signal_label.pack(anchor='w')
        
        self._asset_label = ctk.CTkLabel(
            signal_left,
            text="Capture charts to analyze",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_dim"]
        )
        self._asset_label.pack(anchor='w')
        
        # EXPIRY LABEL - Prominent display
        self._expiry_label = ctk.CTkLabel(
            signal_left,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["accent_yellow"]
        )
        self._expiry_label.pack(anchor='w', pady=(5, 0))
        
        # Right: Confidence ring + Timer
        signal_right = ctk.CTkFrame(signal_row, fg_color="transparent")
        signal_right.pack(side='right')
        
        # Confidence ring
        ring_frame = ctk.CTkFrame(signal_right, fg_color="transparent")
        ring_frame.pack(side='left', padx=(0, 20))
        
        self._confidence_canvas = Canvas(
            ring_frame, width=70, height=70,
            bg=self.colors["card_bg"], highlightthickness=0
        )
        self._confidence_canvas.pack()
        self._draw_confidence_ring(0)
        
        self._confidence_label = ctk.CTkLabel(
            ring_frame,
            text="--",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_dim"]
        )
        self._confidence_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Timer
        timer_frame = ctk.CTkFrame(signal_right, fg_color="transparent")
        timer_frame.pack(side='right')
        
        ctk.CTkLabel(
            timer_frame,
            text="COUNTDOWN",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_dim"]
        ).pack()
        
        self._timer_label = ctk.CTkLabel(
            timer_frame,
            text="--:--",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_gray"]
        )
        self._timer_label.pack()
        
        # === PATTERNS BADGES ===
        self._patterns_frame = ctk.CTkFrame(signal_card, fg_color="transparent")
        self._patterns_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # === WHY TO TRADE (Reasoning) ===
        reason_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=15,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        reason_card.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(
            reason_card,
            text="💡 WHY THIS TRADE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_gray"]
        ).pack(anchor='w', padx=15, pady=(12, 5))
        
        self._reasoning_text = ctk.CTkLabel(
            reason_card,
            text="Waiting for analysis...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_dim"],
            wraplength=420,
            justify='left'
        )
        self._reasoning_text.pack(anchor='w', padx=15, pady=(0, 12))
        
        # === CHART THUMBNAILS ===
        thumbs_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=15,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        thumbs_card.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(
            thumbs_card,
            text="📷 CHART SCREENSHOTS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_gray"]
        ).pack(anchor='w', padx=15, pady=(12, 5))
        
        self._thumbnails_frame = ctk.CTkFrame(thumbs_card, fg_color="transparent")
        self._thumbnails_frame.pack(fill='x', padx=15, pady=(0, 12))
        
        self._thumbs_placeholder = ctk.CTkLabel(
            self._thumbnails_frame,
            text="No captures yet. Press 'aa' to capture.",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_dim"]
        )
        self._thumbs_placeholder.pack(anchor='w')
        
        # === BOTTOM ROW: Stats + Hotkeys + Win/Loss ===
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill='x')
        
        # Hotkeys
        hotkeys_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        hotkeys_frame.pack(side='left')
        
        hotkeys = [("aa", "📸"), ("c", "🔍"), ("v", "👁"), ("x", "🗑")]
        for key, icon in hotkeys:
            ctk.CTkLabel(
                hotkeys_frame,
                text=f"{icon}{key}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors["text_dim"],
                padx=5
            ).pack(side='left')
        
        # Win/Loss buttons
        result_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        result_frame.pack(side='right')
        
        ctk.CTkButton(
            result_frame,
            text="✓ WIN",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            width=60,
            height=28,
            corner_radius=8,
            command=self._record_win
        ).pack(side='left', padx=3)
        
        ctk.CTkButton(
            result_frame,
            text="✗ LOSS",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.colors["accent_red"],
            hover_color="#dc2626",
            width=60,
            height=28,
            corner_radius=8,
            command=self._record_loss
        ).pack(side='left', padx=3)
        
        # Stats - FIX: Create label THEN pack separately
        self._stats_label = ctk.CTkLabel(
            result_frame,
            text="0W / 0L",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_gray"]
        )
        self._stats_label.pack(side='left', padx=(10, 0))
        
        # Close button
        ctk.CTkButton(
            header,
            text="✕",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=self.colors["accent_red"],
            width=30,
            height=30,
            corner_radius=8,
            command=self._on_close
        ).pack(side='right', padx=(10, 0))
        
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.mainloop()
    
    def _draw_confidence_ring(self, percent: int, color: str = None):
        """Draw circular confidence meter"""
        if color is None:
            color = self.colors["text_gray"]
        
        canvas = self._confidence_canvas
        canvas.delete("all")
        
        # Background ring
        canvas.create_arc(
            8, 8, 62, 62,
            start=90, extent=-360,
            outline=self.colors["card_border"],
            width=6, style='arc'
        )
        
        # Progress ring
        if percent > 0:
            extent = -(360 * percent / 100)
            canvas.create_arc(
                8, 8, 62, 62,
                start=90, extent=extent,
                outline=color,
                width=6, style='arc'
            )
        
        # Center text
        canvas.create_text(
            35, 35,
            text=f"{percent}%" if percent > 0 else "--",
            fill=color,
            font=("Segoe UI", 12, "bold")
        )
    
    def _start_drag(self, event):
        """Start window drag"""
        self._drag_x = event.x
        self._drag_y = event.y
    
    def _do_drag(self, event):
        """Handle window drag"""
        x = self._root.winfo_x() + (event.x - self._drag_x)
        y = self._root.winfo_y() + (event.y - self._drag_y)
        self._root.geometry(f"+{x}+{y}")
    
    def _record_win(self):
        """Record a win"""
        self._wins += 1
        self._update_stats()
        self._log_result("WIN")
    
    def _record_loss(self):
        """Record a loss"""
        self._losses += 1
        self._update_stats()
        self._log_result("LOSS")
    
    def _update_stats(self):
        """Update win/loss display"""
        if self._stats_label:
            total = self._wins + self._losses
            winrate = (self._wins / total * 100) if total > 0 else 0
            text = f"{self._wins}W / {self._losses}L ({winrate:.0f}%)"
            
            def _set():
                try:
                    self._stats_label.configure(text=text)
                except:
                    pass
            
            if self._root:
                self._root.after(0, _set)
    
    def _log_result(self, result: str):
        """Log result to CSV"""
        if self._current_signal:
            try:
                with open(self._log_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().isoformat(),
                        self._current_signal.asset,
                        self._current_signal.direction,
                        self._current_signal.confidence,
                        self._current_signal.expiry,
                        ','.join(self._current_signal.patterns_detected or []),
                        self._current_signal.reasoning or '',
                        result
                    ])
            except Exception as e:
                print(f"Log error: {e}")
    
    def _start_timer(self, seconds: int):
        """Start countdown"""
        self._timer_seconds = seconds
        self._timer_running = True
        self._tick_timer()
    
    def _tick_timer(self):
        """Timer tick"""
        if not self._running or not self._timer_running:
            return
        
        if self._timer_seconds > 0:
            mins = self._timer_seconds // 60
            secs = self._timer_seconds % 60
            color = self.colors["accent_green"] if self._timer_seconds > 10 else self.colors["accent_red"]
            
            def _set():
                try:
                    self._timer_label.configure(
                        text=f"{mins:02d}:{secs:02d}",
                        text_color=color
                    )
                except:
                    pass
            
            if self._root:
                self._root.after(0, _set)
            
            self._timer_seconds -= 1
            self._root.after(1000, self._tick_timer)
        else:
            self._timer_running = False
            def _set():
                try:
                    self._timer_label.configure(
                        text="EXPIRED",
                        text_color=self.colors["accent_red"]
                    )
                except:
                    pass
            if self._root:
                self._root.after(0, _set)
    
    def _on_close(self):
        """Close handler"""
        self._running = False
        self._timer_running = False
        self._root.quit()
        self._root.destroy()
    
    # ===== PUBLIC API =====
    
    def update_status(self, status: str, color: str = None):
        """Update status text"""
        if not self._running or not self._status_label:
            return
        
        if color is None:
            color = self.colors["accent_green"]
        
        def _set():
            try:
                self._status_label.configure(text=f"● {status}", text_color=color)
            except:
                pass
        
        if self._root:
            self._root.after(0, _set)
    
    def update_cached_images(self, images: List[CachedImage]):
        """Update chart thumbnails"""
        if not self._running or not self._thumbnails_frame:
            return
        
        self._cached_images = images
        
        def _update():
            try:
                for w in self._thumbnails_frame.winfo_children():
                    w.destroy()
                self._photo_refs = []
                
                if not images:
                    ctk.CTkLabel(
                        self._thumbnails_frame,
                        text="No captures yet. Press 'aa' to capture.",
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["text_dim"]
                    ).pack(anchor='w')
                else:
                    row = ctk.CTkFrame(self._thumbnails_frame, fg_color="transparent")
                    row.pack(fill='x')
                    
                    for i, img in enumerate(images[-4:]):
                        try:
                            if img.path.exists():
                                pil_img = Image.open(img.path)
                                pil_img.thumbnail((95, 60))
                                photo = ImageTk.PhotoImage(pil_img)
                                
                                lbl = ctk.CTkLabel(row, image=photo, text="")
                                lbl.image = photo
                                lbl.pack(side='left', padx=3)
                                self._photo_refs.append(photo)
                        except:
                            ctk.CTkLabel(
                                row,
                                text=f"#{i+1}",
                                font=ctk.CTkFont(size=10),
                                text_color=self.colors["text_dim"]
                            ).pack(side='left', padx=5)
            except Exception as e:
                print(f"Thumbnail error: {e}")
        
        if self._root:
            self._root.after(0, _update)
    
    def show_signal(self, result: AnalysisResult):
        """Display full signal with all details"""
        if not self._running:
            return
        
        signal = result.signal
        self._current_signal = signal
        self._current_result = result
        self._total_signals += 1
        
        def _update():
            try:
                # Signal direction
                if signal.direction == "CALL":
                    color = self.colors["accent_green"]
                    arrow = "▲"
                elif signal.direction == "PUT":
                    color = self.colors["accent_red"]
                    arrow = "▼"
                else:
                    color = self.colors["text_gray"]
                    arrow = "●"
                
                self._signal_label.configure(
                    text=f"{arrow} {signal.direction}",
                    text_color=color
                )
                
                self._asset_label.configure(
                    text=signal.asset,
                    text_color=self.colors["text_white"]
                )
                
                # EXPIRY - Show prominently
                self._expiry_label.configure(
                    text=f"⏱ EXPIRY: {signal.expiry.upper()}",
                    text_color=self.colors["accent_yellow"]
                )
                
                # Confidence ring
                self._draw_confidence_ring(signal.confidence, color)
                
                # Patterns badges
                for w in self._patterns_frame.winfo_children():
                    w.destroy()
                
                if signal.patterns_detected:
                    for pattern in signal.patterns_detected[:4]:
                        ctk.CTkLabel(
                            self._patterns_frame,
                            text=pattern.replace('_', ' ').title(),
                            font=ctk.CTkFont(size=10),
                            fg_color=self.colors["accent_purple"],
                            corner_radius=8,
                            text_color=self.colors["text_white"],
                            padx=8, pady=2
                        ).pack(side='left', padx=2)
                
                # Reasoning - WHY to trade
                reasoning_parts = []
                
                if signal.reasoning:
                    reasoning_parts.append(signal.reasoning)
                
                if signal.key_levels:
                    levels = ", ".join(signal.key_levels[:3])
                    reasoning_parts.append(f"📍 Key levels: {levels}")
                
                if signal.trend_higher_tf:
                    reasoning_parts.append(f"📈 Higher TF: {signal.trend_higher_tf}")
                
                if signal.entry_timing:
                    timing_map = {
                        "now": "▶ Enter immediately",
                        "candle_close": "⏸ Wait for current candle to close",
                        "wait_pullback": "↻ Wait for a pullback before entry"
                    }
                    reasoning_parts.append(timing_map.get(signal.entry_timing, signal.entry_timing))
                
                full_reasoning = "\n".join(reasoning_parts) if reasoning_parts else "AI analysis complete."
                self._reasoning_text.configure(
                    text=full_reasoning,
                    text_color=self.colors["text_white"]
                )
                
                # Timer
                expiry_secs = self._parse_expiry(signal.expiry)
                if expiry_secs > 0:
                    self._start_timer(expiry_secs)
                
                # Log signal
                self._log_signal(signal)
                
            except Exception as e:
                print(f"Signal display error: {e}")
        
        if self._root:
            self._root.after(0, _update)
    
    def _parse_expiry(self, expiry: str) -> int:
        """Parse expiry to seconds"""
        try:
            expiry = expiry.lower().strip()
            if 's' in expiry:
                return int(expiry.replace('s', ''))
            elif 'm' in expiry:
                return int(expiry.replace('m', '')) * 60
            return 60
        except:
            return 60
    
    def _log_signal(self, signal: TradingSignal):
        """Log signal to CSV (without result yet)"""
        try:
            with open(self._log_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    signal.asset,
                    signal.direction,
                    signal.confidence,
                    signal.expiry,
                    ','.join(signal.patterns_detected or []),
                    signal.reasoning or '',
                    'PENDING'
                ])
        except:
            pass
    
    def show_error(self, error_msg: str):
        """Display error"""
        if not self._running:
            return
        
        def _update():
            try:
                self._signal_label.configure(
                    text="⚠ ERROR",
                    text_color=self.colors["accent_red"]
                )
                self._asset_label.configure(
                    text="Analysis failed",
                    text_color=self.colors["text_dim"]
                )
                self._draw_confidence_ring(0, self.colors["accent_red"])
                
                err = error_msg[:150] + "..." if len(error_msg) > 150 else error_msg
                self._reasoning_text.configure(
                    text=f"Error: {err}\n\nImages kept in cache. Press 'v' to view, 'c' to retry.",
                    text_color=self.colors["accent_red"]
                )
            except:
                pass
        
        if self._root:
            self._root.after(0, _update)
    
    def clear_signal(self):
        """Reset to waiting state"""
        if not self._running:
            return
        
        self._timer_running = False
        
        def _update():
            try:
                self._signal_label.configure(
                    text="WAITING",
                    text_color=self.colors["text_gray"]
                )
                self._asset_label.configure(
                    text="Capture charts to analyze",
                    text_color=self.colors["text_dim"]
                )
                self._draw_confidence_ring(0)
                self._timer_label.configure(
                    text="--:--",
                    text_color=self.colors["text_gray"]
                )
                self._reasoning_text.configure(
                    text="Waiting for analysis...",
                    text_color=self.colors["text_dim"]
                )
                for w in self._patterns_frame.winfo_children():
                    w.destroy()
            except:
                pass
        
        if self._root:
            self._root.after(0, _update)


# Global instance
sidebar = ModernTradingPanel()


if __name__ == "__main__":
    sidebar.start()
    import time
    time.sleep(60)
