"""
Groq Vision analyzer - Fallback #2 (Free tier)
"""
import json
import base64
from pathlib import Path
from typing import List
import time

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from config import GROQ_API_KEY, AI_TIMEOUT_SECONDS
from .prompt_templates import SYSTEM_PROMPT, get_analysis_prompt
from .signal_model import TradingSignal, AnalysisResult, create_no_trade_signal


def is_available() -> bool:
    """Check if Groq is available and configured"""
    return GROQ_AVAILABLE and bool(GROQ_API_KEY)


def _encode_image(image_path: Path) -> str:
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_mime_type(path: Path) -> str:
    """Get MIME type from file extension"""
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }.get(suffix, "image/png")


def _parse_response(response_text: str) -> TradingSignal:
    """Parse AI response JSON into TradingSignal"""
    try:
        text = response_text.strip()
        if text.startswith("```"):
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
            payout_percent=float(str(data.get("payout_percent", 0)).replace('%', '').strip() or 0),
            timeframes_analyzed=data.get("timeframes_analyzed", []),
            patterns_detected=data.get("patterns_detected", []),
            trend_higher_tf=data.get("trend_higher_tf", ""),
            trend_lower_tf=data.get("trend_lower_tf", ""),
            key_levels=data.get("key_levels", []),
            reasoning=data.get("reasoning", "")
        )
    except json.JSONDecodeError as e:
        return create_no_trade_signal(f"Failed to parse response: {str(e)}")


def analyze(image_paths: List[Path]) -> AnalysisResult:
    """
    Analyze chart images using Groq's vision model.
    
    Note: Groq's vision support is via llama-3.2-90b-vision-preview or similar.
    
    Args:
        image_paths: List of paths to chart screenshots
        
    Returns:
        AnalysisResult with signal and metadata
    """
    if not is_available():
        return AnalysisResult(
            signal=create_no_trade_signal("Groq not available"),
            provider_used="groq",
            analysis_time_ms=0,
            images_analyzed=len(image_paths),
            error="Groq API key not configured"
        )
    
    start_time = time.time()
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build message content with images
        content = []
        
        # Add images (Groq vision models support this format)
        for path in image_paths:
            base64_image = _encode_image(path)
            mime_type = _get_mime_type(path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            })
        
        # Add text prompt  
        content.append({
            "type": "text",
            "text": get_analysis_prompt(len(image_paths))
        })
        
        # Make API call - using llama vision model
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content}
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        response_text = response.choices[0].message.content
        signal = _parse_response(response_text)
        
        return AnalysisResult(
            signal=signal,
            provider_used="groq",
            analysis_time_ms=elapsed_ms,
            images_analyzed=len(image_paths),
            raw_response=response_text
        )
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        print(f"Groq error: {error_msg}")
        
        return AnalysisResult(
            signal=create_no_trade_signal(f"Groq error: {error_msg}"),
            provider_used="groq",
            analysis_time_ms=elapsed_ms,
            images_analyzed=len(image_paths),
            error=error_msg
        )


if __name__ == "__main__":
    print(f"Groq available: {is_available()}")
