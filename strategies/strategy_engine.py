"""
Strategy Templates System
==========================
Define and manage trading strategies with custom prompts and rules
"""
from typing import Dict, List, Optional
import json
from pathlib import Path

# Strategy definitions storage
STRATEGIES_DIR = Path(__file__).parent / "configs"
STRATEGIES_DIR.mkdir(exist_ok=True)


# Built-in strategy templates
BUILTIN_STRATEGIES = {
    "conservative": {
        "name": "Conservative",
        "description": "High confidence, longer expiries, requires patterns",
        "rules": {
            "min_confidence": 80,
            "max_confidence": 100,
            "allowed_expiry": ["2m", "5m", "15m", "30m"],
            "preferred_expiry": "15m",
            "patterns_required": True,
            "timeframe_confluence_required": True,
            "min_timeframes": 3,
            "avoid_high_volatility": True
        },
        "prompt_modifiers": {
            "confidence_boost": "Be extra conservative. Only suggest signals with very high confidence (80%+).",
            "pattern_emphasis": "Require clear, well-formed patterns. Avoid weak or incomplete patterns.",
            "expiry_guidance": "Prefer 5-minute expiry for better confirmation. Avoid very short timeframes.",
            "risk_reminder": "This is a conservative strategy - better to skip than take risky trades."
        }
    },
    
    "scalping": {
        "name": "Scalping",
        "description": "Fast trades, 1-2m expiry only, high frequency",
        "rules": {
            "min_confidence": 70,
            "max_confidence": 100,
            "allowed_expiry": ["1m", "2m"],
            "preferred_expiry": "1m",
            "patterns_required": False,  # Can trade on momentum
            "timeframe_confluence_required": False,
            "min_timeframes": 1,
            "avoid_high_volatility": False
        },
        "prompt_modifiers": {
            "confidence_boost": "Look for quick scalping opportunities. 70%+ confidence is acceptable.",
            "pattern_emphasis": "Strong momentum is more important than perfect patterns.",
            "expiry_guidance": "Focus on 1-2 minute expiries. Quick in and out.",
            "risk_reminder": "Scalping strategy - expect more trades, manage risk per trade."
        }
    },
    
    "aggressive": {
        "name": "Aggressive",
        "description": "Lower confidence threshold, more trades, higher risk",
        "rules": {
            "min_confidence": 65,
            "max_confidence": 100,
            "allowed_expiry": ["1m", "2m", "5m"],
            "preferred_expiry": "2m",
            "patterns_required": False,
            "timeframe_confluence_required": False,
            "min_timeframes": 2,
            "avoid_high_volatility": False
        },
        "prompt_modifiers": {
            "confidence_boost": "Take more trading opportunities. 65%+ confidence is acceptable.",
            "pattern_emphasis": "Even weak patterns can be traded if trend is clear.",
            "expiry_guidance": "1-2 minute expiries preferred for quick entries.",
            "risk_reminder": "Aggressive strategy - expect more trades and manage position sizes."
        }
    },
    
    "swing": {
        "name": "Swing Trading",
        "description": "Longer timeframes, bigger moves, 15m+ expiry",
        "rules": {
            "min_confidence": 75,
            "max_confidence": 100,
            "allowed_expiry": ["5m", "15m", "30m", "1h"],
            "preferred_expiry": "30m",
            "patterns_required": True,
            "timeframe_confluence_required": True,
            "min_timeframes": 3,
            "avoid_high_volatility": False  # Volatility OK for swings
        },
        "prompt_modifiers": {
            "confidence_boost": "Look for strong trend continuation or reversal setups.",
            "pattern_emphasis": "Multi-candle patterns (morning/evening star, three soldiers) preferred.",
            "expiry_guidance": "Focus on 15-30 minute expiries for swing moves.",
            "risk_reminder": "Swing strategy - fewer trades but larger moves expected."
        }
    },
    
    "trend_following": {
        "name": "Trend Following",
        "description": "Only trade WITH the trend, requires confluence",
        "rules": {
            "min_confidence": 75,
            "max_confidence": 100,
            "allowed_expiry": ["2m", "5m", "15m"],
            "preferred_expiry": "5m",
            "patterns_required": True,
            "timeframe_confluence_required": True,  # MUST have all TFs agreeing
            "min_timeframes": 3,
            "avoid_high_volatility": True
        },
        "prompt_modifiers": {
            "confidence_boost": "ONLY suggest signals that align with the trend on ALL timeframes.",
            "pattern_emphasis": "Look for continuation patterns in the direction of the trend.",
            "expiry_guidance": "5-minute expiry preferred to let trend develop.",
            "risk_reminder": "Trend following strategy - wait for clear trends, skip ranging markets."
        }
    }
}


class StrategyEngine:
    """Manages trading strategies and signal filtering"""
    
    def __init__(self):
        self.active_strategy = "conservative"
        self.custom_strategies = self.load_custom_strategies()
    
    def load_custom_strategies(self) -> Dict:
        """Load user-created strategies from disk"""
        custom = {}
        for file in STRATEGIES_DIR.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    strategy = json.load(f)
                    custom[file.stem] = strategy
            except Exception as e:
                print(f"Error loading strategy {file}: {e}")
        return custom
    
    def get_all_strategies(self) -> Dict:
        """Get all available strategies (builtin + custom)"""
        return {**BUILTIN_STRATEGIES, **self.custom_strategies}
    
    def get_strategy(self, name: str) -> Optional[Dict]:
        """Get specific strategy by name"""
        all_strategies = self.get_all_strategies()
        return all_strategies.get(name)
    
    def set_active_strategy(self, name: str):
        """Set the active strategy"""
        if name in self.get_all_strategies():
            self.active_strategy = name
            return True
        return False
    
    def get_active_strategy(self) -> Dict:
        """Get currently active strategy"""
        return self.get_strategy(self.active_strategy)
    
    def filter_signal(self, signal_data: dict) -> tuple[bool, Optional[str]]:
        """
        Check if signal passes active strategy rules
        
        Returns:
            (passes, reason)
        """
        strategy = self.get_active_strategy()
        if not strategy:
            return True, None  # No strategy = allow all
        
        rules = strategy.get('rules', {})
        
        # Check confidence
        confidence = signal_data.get('confidence', 0)
        min_conf = rules.get('min_confidence', 0)
        if confidence < min_conf:
            return False, f"Confidence {confidence}% below strategy minimum {min_conf}%"
        
        # Check expiry
        expiry = signal_data.get('expiry', '')
        allowed_expiry = rules.get('allowed_expiry', [])
        if allowed_expiry and expiry not in allowed_expiry:
            return False, f"Expiry {expiry} not allowed by strategy (allowed: {', '.join(allowed_expiry)})"
        
        # Check patterns required
        if rules.get('patterns_required', False):
            patterns = signal_data.get('patterns_detected', [])
            if not patterns or len(patterns) == 0:
                return False, "Strategy requires patterns but none detected"
        
        # All checks passed
        return True, None
    
    def get_prompt_modifiers(self) -> str:
        """Get AI prompt modifications for active strategy"""
        strategy = self.get_active_strategy()
        if not strategy:
            return ""
        
        modifiers = strategy.get('prompt_modifiers', {})
        
        prompt_addition = "\n\n## ACTIVE STRATEGY RULES:\n\n"
        prompt_addition += f"**Strategy:** {strategy.get('name', 'Unknown')}\n\n"
        
        for key, value in modifiers.items():
            prompt_addition += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        # Add rules
        rules = strategy.get('rules', {})
        prompt_addition += f"\n**Required Confidence:** {rules.get('min_confidence', 70)}%+\n"
        prompt_addition += f"**Preferred Expiry:** {rules.get('preferred_expiry', 'any')}\n"
        
        return prompt_addition
    
    def save_custom_strategy(self, name: str, strategy: Dict) -> bool:
        """Save a custom strategy"""
        try:
            file_path = STRATEGIES_DIR / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(strategy, f, indent=2)
            
            # Reload custom strategies
            self.custom_strategies = self.load_custom_strategies()
            return True
        except Exception as e:
            print(f"Error saving strategy: {e}")
            return False
    
    def delete_custom_strategy(self, name: str) -> bool:
        """Delete a custom strategy"""
        try:
            file_path = STRATEGIES_DIR / f"{name}.json"
            if file_path.exists() and name not in BUILTIN_STRATEGIES:
                file_path.unlink()
                self.custom_strategies = self.load_custom_strategies()
                return True
            return False
        except Exception as e:
            print(f"Error deleting strategy: {e}")
            return False


# Global strategy engine
strategy_engine = StrategyEngine()
