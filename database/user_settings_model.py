"""
User Settings Database Models
==============================
Stores user preferences and risk settings
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSettings:
    """User risk management settings"""
    id: int = 1  # Single user for now
    
    # Account Details
    account_balance: float = 1000.0
    currency: str = "USD"
    
    # Risk Parameters
    risk_per_trade_percent: float = 2.0
    max_daily_loss_percent: float = 5.0
    max_consecutive_losses: int = 3
    
    # Trading Style
    trading_style: str = "conservative"  # scalping, conservative, aggressive
    
    # Goals
    daily_profit_target: float = 50.0
    monthly_profit_target: float = 1000.0
    
    # Auto-stop
    auto_stop_enabled: bool = True
    stop_on_daily_limit: bool = True
    stop_on_consecutive_losses: bool = True
    
    def to_dict(self):
        return {
            'account_balance': self.account_balance,
            'currency': self.currency,
            'risk_per_trade_percent': self.risk_per_trade_percent,
            'max_daily_loss_percent': self.max_daily_loss_percent,
            'max_consecutive_losses': self.max_consecutive_losses,
            'trading_style': self.trading_style,
            'daily_profit_target': self.daily_profit_target,
            'monthly_profit_target': self.monthly_profit_target,
            'auto_stop_enabled': self.auto_stop_enabled,
            'stop_on_daily_limit': self.stop_on_daily_limit,
            'stop_on_consecutive_losses': self.stop_on_consecutive_losses
        }
