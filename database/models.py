"""
Database Models for AI Trading Analyst
======================================
SQLite database for persistent storage
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Signal:
    """Trading signal record"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    direction: str = ""
    asset: str = ""
    confidence: int = 0
    expiry: str = ""
    entry_timing: str = ""
    reasoning: str = ""
    patterns_detected: str = ""  # JSON string
    key_levels: str = ""  # JSON string
    trend_higher_tf: str = ""
    trend_lower_tf: str = ""
    provider_used: str = ""
    analysis_time_ms: int = 0
    
    # Trade result
    result: Optional[str] = None  # 'win', 'loss', 'skip', None
    user_note: Optional[str] = None
    
    # Chart references
    chart_paths: str = ""  # JSON string of image paths


@dataclass
class TradeStats:
    """Aggregated statistics"""
    total_signals: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_skips: int = 0
    win_rate: float = 0.0
    
    # By asset
    stats_by_asset: str = ""  # JSON
    
    # By pattern
    stats_by_pattern: str = ""  # JSON
    
    # By timeframe
    stats_by_expiry: str = ""  # JSON
