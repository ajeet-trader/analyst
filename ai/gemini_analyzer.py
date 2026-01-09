"""
Gemini Vision analyzer - Primary AI provider
"""
import json
import base64
from pathlib import Path
from typing import List, Optional
import time
import warnings

# Suppress the deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config import GEMINI_API_KEY, AI_TIMEOUT_SECONDS
from .prompt_templates import SYSTEM_PROMPT, get_analysis_prompt
from .signal_model import TradingSignal, AnalysisResult, create_no_trade_signal


def is_available() -> bool:
    """Check if Gemini is available and configured"""
    return GEMINI_AVAILABLE and bool(GEMINI_API_KEY)


def _load_image_as_part(image_path: Path) -> dict:
    """Load image and convert to Gemini format"""
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Determine mime type
    suffix = image_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }.get(suffix, "image/png")
    
    return {
        "mime_type": mime_type,
        "data": image_data
    }


def _parse_response(response_text: str) -> TradingSignal:
    """Parse AI response JSON into TradingSignal"""
    try:
        # Clean up response - remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            # Remove code block markers
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines)
        
        data = json.loads(text)
        
        return TradingSignal(
            direction=data.get("direction", "NO_TRADE"),
            confidence=int(data.get("confidence", 0)),
            expiry=data.get("expiry", ""),
            entry_timing=data.get("entry_timing", "now"),
            asset=data.get("asset", "Unknown"),
            timeframes_analyzed=data.get("timeframes_analyzed", []),
            patterns_detected=data.get("patterns_detected", []),
            trend_higher_tf=data.get("trend_higher_tf", ""),
            trend_lower_tf=data.get("trend_lower_tf", ""),
            key_levels=data.get("key_levels", []),
            reasoning=data.get("reasoning", "")
        )
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response_text[:500]}")
        return create_no_trade_signal(f"Failed to parse AI response: {str(e)}")


def analyze(image_paths: List[Path]) -> AnalysisResult:
    """
    Analyze chart images using Gemini Vision.
    
    Args:
        image_paths: List of paths to chart screenshots
        
    Returns:
        AnalysisResult with signal and metadata
    """
    if not is_available():
        return AnalysisResult(
            signal=create_no_trade_signal("Gemini not available"),
            provider_used="gemini",
            analysis_time_ms=0,
            images_analyzed=len(image_paths),
            error="Gemini API key not configured"
        )
    
    start_time = time.time()
    
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        
        # Build content with images
        content_parts = []
        
        # Add images first
        for path in image_paths:
            img_part = _load_image_as_part(path)
            content_parts.append(img_part)
        
        # Add text prompt
        full_prompt = SYSTEM_PROMPT + "\n\n" + get_analysis_prompt(len(image_paths))
        content_parts.append(full_prompt)
        
        # Generate response
        response = model.generate_content(
            content_parts,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
            }
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Parse response
        response_text = response.text
        signal = _parse_response(response_text)
        
        return AnalysisResult(
            signal=signal,
            provider_used="gemini",
            analysis_time_ms=elapsed_ms,
            images_analyzed=len(image_paths),
            raw_response=response_text
        )
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        print(f"Gemini error: {error_msg}")
        
        return AnalysisResult(
            signal=create_no_trade_signal(f"Gemini error: {error_msg}"),
            provider_used="gemini",
            analysis_time_ms=elapsed_ms,
            images_analyzed=len(image_paths),
            error=error_msg
        )


if __name__ == "__main__":
    print(f"Gemini available: {is_available()}")
    if GEMINI_AVAILABLE:
        print("google-generativeai package is installed")
    if GEMINI_API_KEY:
        print("API key is configured")
