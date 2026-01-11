"""
Together AI Vision Analyzer
Uses free tier of Together AI with Llama 3.2 Vision
"""
from together import Together
from pathlib import Path
from typing import List
import base64

from config import TOGETHER_API_KEY
from ai.signal_model import TradingSignal, AnalysisResult
from ai.prompt_templates import get_analysis_prompt, SYSTEM_PROMPT

def is_available() -> bool:
    """Check if Together AI is available"""
    return bool(TOGETHER_API_KEY)


class TogetherAnalyzer:
    """Free tier Together AI with Llama 3.2 Vision"""
    
    def __init__(self):
        self.client = Together(api_key=TOGETHER_API_KEY) if TOGETHER_API_KEY else None
        self.model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
    
    def is_available(self) -> bool:
        """Check if Together AI is configured"""
        return self.client is not None
    
    def analyze(self, image_paths: List[Path]) -> AnalysisResult:
        """Analyze charts using Together AI"""
        if not self.is_available():
            return AnalysisResult(
                success=False,
                error="Together AI key not configured"
            )
        
        try:
            import time
            start = time.time()
            
            # Convert images to base64
            image_data = []
            for img_path in image_paths[:3]:
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    image_data.append(f"data:image/png;base64,{b64}")
            
            # Build messages
            content = [{"type": "text", "text": get_analysis_prompt(len(image_paths))}]
            for img in image_data:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            
            # API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            signal = self._parse_response(response_text)
            
            return AnalysisResult(
                success=True,
                signal=signal,
                provider_used="together",
                model_used=self.model,
                analysis_time_ms=int((time.time() - start) * 1000)
            )
        
        except Exception as e:
            return AnalysisResult(
                success=False,
                error=f"Together AI error: {str(e)}"
            )
    
    def _parse_response(self, text: str) -> TradingSignal:
        """Parse AI response"""
        text_lower = text.lower()
        
        # Direction
        if "call" in text_lower or "buy" in text_lower:
            direction = "CALL"
        elif "put" in text_lower or "sell" in text_lower:
            direction = "PUT"
        else:
            direction = "NO TRADE"
        
        # Confidence
        import re
        confidence = 70
        conf_match = re.search(r'(\d{1,3})%', text)
        if conf_match:
            confidence = int(conf_match.group(1))
        
        # Asset
        asset = "Unknown"
        for line in text.split('\n'):
            if 'asset' in line.lower() or 'pair' in line.lower():
                asset = line.split(':')[-1].strip() if ':' in line else asset
                break
        
        # Expiry
        expiry = "1m"
        if "5" in text and ("min" in text_lower or "m" in text_lower):
            expiry = "5m"
        elif "2" in text and ("min" in text_lower or "m" in text_lower):
            expiry = "2m"
        
        # Patterns
        patterns = []
        keywords = ["engulfing", "doji", "hammer", "support", "resistance", "breakout"]
        for kw in keywords:
            if kw in text_lower:
                patterns.append(kw)
        
        # Timing
        timing = "now"
        if "wait" in text_lower and "candle" in text_lower:
            timing = "candle_close"
        
        # Payout
        payout = 0.0
        payout_match = re.search(r'payout.*?(\d{1,3})', text_lower)
        if payout_match:
            payout = float(payout_match.group(1))
            
        return TradingSignal(
            direction=direction,
            confidence=min(confidence, 95),
            expiry=expiry,
            entry_timing=timing,
            asset=asset,
            payout_percent=payout,
            reasoning=text[:200],
            patterns_detected=patterns[:4] if patterns else None
        )


if __name__ == "__main__":
    analyzer = TogetherAnalyzer()
    print(f"Available: {analyzer.is_available()}")
