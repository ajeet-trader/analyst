"""
Windows Toast Notification for Signals
Simple, native Windows notifications
"""
from winotify import Notification, audio
from ai.signal_model import TradingSignal


def show_notification(signal: TradingSignal, auto_dismiss: int = 15):
    """
    Show Windows toast notification for signal
    
    Args:
        signal: Trading signal
        auto_dismiss: Seconds before auto-dismiss (ignored, uses Windows default)
    """
    # Always print to console
    arrow = "▲" if signal.direction == "CALL" else "▼" if signal.direction == "PUT" else "●"
    print(f"\n🔔 {arrow} {signal.direction} | {signal.asset} | {signal.confidence}% | {signal.expiry}")
    
    try:
        # Create notification
        toast = Notification(
            app_id="AI Trading Analyst",
            title=f"{signal.direction} Signal - {signal.asset}",
            msg=f"Confidence: {signal.confidence}% | Expiry: {signal.expiry}\n{signal.reasoning[:100] if signal.reasoning else 'No details'}",
            duration="long"
        )
        
        # Set audio based on direction
        if signal.direction == "CALL":
            toast.set_audio(audio.LoopingAlarm, loop=False)
        elif signal.direction == "PUT":
            toast.set_audio(audio.LoopingAlarm2, loop=False)
        
        # Show notification
        toast.show()
        print("✅ Desktop notification sent")
        
    except Exception as e:
        print(f"⚠️ Notification failed: {e}")


if __name__ == "__main__":
    # Test
    from ai.signal_model import TradingSignal
    
    test_signal = TradingSignal(
        direction="CALL",
        confidence=85,
        expiry="1m",
        entry_timing="now",
        asset="EUR/USD",
        reasoning="Strong bullish momentum with support bounce",
        patterns_detected=["bullish_engulfing"]
    )
    
    show_notification(test_signal)
