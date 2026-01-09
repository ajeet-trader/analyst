"""
Signal Overlay - Disabled (signals shown in main panel)
"""
from ai.signal_model import TradingSignal
from config import SIGNAL_DISPLAY_DURATION


def show_signal_overlay(signal: TradingSignal, duration: int = SIGNAL_DISPLAY_DURATION):
    """Overlay disabled - signals show in main panel"""
    # Overlay functionality moved to main panel
    pass
