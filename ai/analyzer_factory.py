"""
AI Analyzer Factory - Provider selection with automatic fallback
"""
from pathlib import Path
from typing import List, Optional
import time

from . import gemini_analyzer
from . import openai_analyzer
from . import groq_analyzer
from . import huggingface_analyzer
from . import together_analyzer
from .signal_model import TradingSignal, AnalysisResult, create_no_trade_signal

from config import (
    AI_MAX_RETRIES,
    ENABLE_GROQ,
    ENABLE_HUGGINGFACE,
    ENABLE_TOGETHER,
    ENABLE_GEMINI,
    ENABLE_OPENAI
)


# Provider priority order (FREE FIRST!)
PROVIDERS = [
    ("groq", groq_analyzer, ENABLE_GROQ),
    ("huggingface", huggingface_analyzer, ENABLE_HUGGINGFACE),
    ("together", together_analyzer, ENABLE_TOGETHER),
    ("gemini", gemini_analyzer, ENABLE_GEMINI),
    ("openai", openai_analyzer, ENABLE_OPENAI),
]


def get_available_providers() -> List[str]:
    """Get list of available/configured providers"""
    available = []
    for name, module, enabled in PROVIDERS:
        if enabled and module.is_available():
            available.append(name)
    return available


def analyze_charts(
    image_paths: List[Path],
    preferred_provider: Optional[str] = None
) -> AnalysisResult:
    """
    Analyze chart images using available AI providers.
    
    Tries providers in order with automatic fallback on errors.
    
    Args:
        image_paths: List of paths to chart screenshots
        preferred_provider: Optional specific provider to try first
        
    Returns:
        AnalysisResult with signal and metadata
    """
    if not image_paths:
        return AnalysisResult(
            signal=create_no_trade_signal("No images provided"),
            provider_used="none",
            analysis_time_ms=0,
            images_analyzed=0,
            error="No images to analyze"
        )
    
    # Build provider order
    providers_to_try = []
    
    # Add preferred provider first if specified and available
    if preferred_provider:
        for name, module, enabled in PROVIDERS:
            if name == preferred_provider and enabled and module.is_available():
                providers_to_try.append((name, module))
                break
    
    # Add remaining providers
    for name, module, enabled in PROVIDERS:
        if enabled and module.is_available() and (name, module) not in providers_to_try:
            providers_to_try.append((name, module))
    
    if not providers_to_try:
        return AnalysisResult(
            signal=create_no_trade_signal("No AI providers available"),
            provider_used="none",
            analysis_time_ms=0,
            images_analyzed=len(image_paths),
            error="No AI providers configured. Please set up API keys in .env"
        )
    
    # Try each provider
    last_error = None
    for name, module in providers_to_try:
        print(f"🤖 Trying {name}...")
        
        for attempt in range(AI_MAX_RETRIES):
            result = module.analyze(image_paths)
            
            if result.success:
                print(f"✅ {name} analysis complete in {result.analysis_time_ms}ms")
                return result
            else:
                last_error = result.error
                print(f"⚠️ {name} attempt {attempt + 1} failed: {result.error}")
                
                if attempt < AI_MAX_RETRIES - 1:
                    time.sleep(1)  # Brief delay before retry
        
        print(f"❌ {name} failed after {AI_MAX_RETRIES} attempts")
    
    # All providers failed
    return AnalysisResult(
        signal=create_no_trade_signal(f"All providers failed: {last_error}"),
        provider_used="none",
        analysis_time_ms=0,
        images_analyzed=len(image_paths),
        error=f"All AI providers failed. Last error: {last_error}"
    )


def test_providers():
    """Test connectivity to all configured providers"""
    print("\n🔍 Testing AI Providers...")
    print("-" * 40)
    
    available = get_available_providers()
    
    for name, module, enabled in PROVIDERS:
        if not enabled:
            status = "⚫ Disabled"
        elif name in available:
            status = "✅ Available"
        else:
            status = "❌ Not configured"
        print(f"  {name}: {status}")
    
    print("-" * 40)
    
    if available:
        print(f"Primary provider: {available[0]}")
        if len(available) > 1:
            print(f"Fallbacks: {', '.join(available[1:])}")
    else:
        print("⚠️ No providers configured! Please set API keys in .env")
    
    return available


if __name__ == "__main__":
    test_providers()
