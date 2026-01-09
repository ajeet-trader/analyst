"""
HuggingFace Vision Analyzer
Uses Moondream2 or Llama 3.2 Vision via HuggingFace Inference API (FREE)
"""
from huggingface_hub import InferenceClient
from pathlib import Path
from typing import List, Optional
import base64

from config import HUGGINGFACE_TOKEN
from ai.signal_model import TradingSignal, AnalysisResult
from ai.prompt_templates import get_analysis_prompt

def is_available() -> bool:
    """Check if HuggingFace is available"""
    return bool(HUGGINGFACE_TOKEN)


class HuggingFaceAnalyzer:
    """
    Free vision analysis using HuggingFace models.
    Priority: Moondream2 (fast) -> Llama 3.2 Vision (accurate)
    """
    
    def __init__(self):
        self.client = InferenceClient(token=HUGGINGFACE_TOKEN) if HUGGINGFACE_TOKEN else None
        # Free models on HF
        self.models = [
            "vikhyatk/moondream2",  # Fast, small
            "meta-llama/Llama-3.2-11B-Vision-Instruct"  # Accurate, larger
        ]
    
    def is_available(self) -> bool:
        """Check if HuggingFace is configured"""
        return self.client is not None
    
    def analyze(self, image_paths: List[Path]) -> AnalysisResult:
        """Analyze charts using HuggingFace vision models"""
        if not self.is_available():
            return AnalysisResult(
                success=False,
                error="HuggingFace token not configured"
            )
        
        try:
            # Prepare images
            images = []
            for img_path in image_paths:
                with open(img_path, "rb") as f:
                    images.append(f.read())
            
            # Try models in priority order
            for model in self.models:
                try:
                    result = self._analyze_with_model(model, images)
                    if result.success:
                        return result
                except Exception as e:
                    print(f"HF model {model} failed: {e}")
                    continue
            
            return AnalysisResult(
                success=False,
                error="All HuggingFace models failed"
            )
        
        except Exception as e:
            return AnalysisResult(
                success=False,
                error=f"HuggingFace error: {str(e)}"
            )
    
    def _analyze_with_model(self, model: str, images: List[bytes]) -> AnalysisResult:
        """Analyze with specific model"""
        import time
        start = time.time()
        
        # Get prompt
        prompt = get_analysis_prompt(len(images))
        
        # For moondream2 - simpler prompt
        if "moondream" in model.lower():
            result = self.client.image_to_text(
                images[0],  # Use first image
                model=model,
                prompt=prompt
            )
            response_text = result if isinstance(result, str) else result.generated_text
        
        # For Llama Vision - chat format
        else:
            # Convert images to base64
            import base64
            img_b64 = [base64.b64encode(img).decode() for img in images[:3]]
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img}"}
                        } for img in img_b64
                    ]
                }
            ]
            
            result = self.client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=500
            )
            response_text = result.choices[0].message.content
        
        # Parse response
        signal = self._parse_response(response_text)
        
        return AnalysisResult(
            success=True,
            signal=signal,
            provider_used="huggingface",
            model_used=model,
            analysis_time_ms=int((time.time() - start) * 1000)
        )
    
    def _parse_response(self, text: str) -> TradingSignal:
        """Parse AI response into trading signal"""
        # Simple parsing - look for key indicators
        text_lower = text.lower()
        
        # Direction
        if "call" in text_lower or "buy" in text_lower or "bullish" in text_lower:
            direction = "CALL"
        elif "put" in text_lower or "sell" in text_lower or "bearish" in text_lower:
            direction = "PUT"
        else:
            direction = "NO TRADE"
        
        # Extract confidence (look for percentage)
        confidence = 70  # Default
        import re
        conf_match = re.search(r'(\d{1,3})%', text)
        if conf_match:
            confidence = int(conf_match.group(1))
        
        # Extract asset
        asset = "Unknown Asset"
        for line in text.split('\n'):
            if 'asset' in line.lower() or 'pair' in line.lower():
                asset = line.split(':')[-1].strip() if ':' in line else asset
                break
        
        # Extract expiry
        expiry = "1m"  # Default
        if "5 min" in text_lower or "5m" in text_lower:
            expiry = "5m"
        elif "2 min" in text_lower or "2m" in text_lower:
            expiry = "2m"
        
        # Extract patterns
        patterns = []
        pattern_keywords = [
            "engulfing", "doji", "hammer", "shooting star", 
            "support", "resistance", "breakout", "pullback"
        ]
        for keyword in pattern_keywords:
            if keyword in text_lower:
                patterns.append(keyword.replace(" ", "_"))
        
        # Entry timing
        timing = "now"
        if "wait" in text_lower:
            if "candle" in text_lower:
                timing = "candle_close"
            else:
                timing = "wait_pullback"
        
        return TradingSignal(
            direction=direction,
            confidence=min(confidence, 95),
            expiry=expiry,
            entry_timing=timing,
            asset=asset,
            reasoning=text[:200],
            patterns_detected=patterns[:4] if patterns else None
        )


if __name__ == "__main__":
    # Test
    analyzer = HuggingFaceAnalyzer()
    print(f"Available: {analyzer.is_available()}")
