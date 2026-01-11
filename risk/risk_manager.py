"""
Risk Management System
=======================
Calculate position sizes, track limits, provide recommendations
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from database import db


class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict:
        """Load user risk settings from database"""
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            # Return defaults
            return {
                'account_balance': 1000.0,
                'risk_per_trade_percent': 2.0,
                'max_daily_loss_percent': 5.0,
                'max_consecutive_losses': 3,
                'trading_style': 'conservative',
                'daily_profit_target': 50.0,
                'auto_stop_enabled': True
            }
    
    def calculate_position_size(self, confidence: int = 80) -> Dict:
        """
        Calculate recommended position size
        
        Returns:
            {
                'recommended_size': float,
                'max_loss': float,
                'risk_reward': str,
                'account_risk_percent': float
            }
        """
        balance = self.settings['account_balance']
        risk_percent = self.settings['risk_per_trade_percent']
        
        # Base position size
        base_size = balance * (risk_percent / 100)
        
        # Adjust based on confidence (optional)
        # Higher confidence = can risk slightly more
        confidence_multiplier = 0.5 + (confidence / 100) * 0.5  # 0.5 to 1.0
        recommended_size = base_size * confidence_multiplier
        
        # Cap at risk percent
        recommended_size = min(recommended_size, balance * (risk_percent / 100))
        
        return {
            'recommended_size': round(recommended_size, 2),
            'max_loss': round(recommended_size, 2),  # For binary options, max loss = position size
            'risk_reward': '1:0.8',  # Typical binary options payout ~80%
            'account_risk_percent': round((recommended_size / balance) * 100, 2)
        }
    
    def check_daily_status(self) -> Dict:
        """
        Check today's trading status
        
        Returns:
            {
                'can_trade': bool,
                'trades_today': int,
                'pnl_today': float,
                'daily_limit_hit': bool,
                'consecutive_losses': int,
                'warning': str or None
            }
        """
        cursor = db.conn.cursor()
        today = datetime.now().date()
        
        # Get today's trades
        cursor.execute("""
            SELECT result, confidence 
            FROM signals 
            WHERE DATE(timestamp) = ? 
            AND result IS NOT NULL
            ORDER BY timestamp DESC
        """, (str(today),))
        
        trades = cursor.fetchall()
        trades_today = len(trades)
        
        # Calculate P&L (simplified - assumes Fixed payout)
        wins = sum(1 for t in trades if t['result'] == 'win')
        losses = sum(1 for t in trades if t['result'] == 'loss')
        
        # Assume 2% risk per trade, 80% payout
        balance = self.settings['account_balance']
        risk_per_trade = balance * (self.settings['risk_per_trade_percent'] / 100)
        
        pnl_today = (wins * risk_per_trade * 0.8) - (losses * risk_per_trade)
        
        # Check consecutive losses
        consecutive_losses = 0
        for trade in trades:
            if trade['result'] == 'loss':
                consecutive_losses += 1
            else:
                break
        
        # Check limits
        daily_loss_limit = balance * (self.settings['max_daily_loss_percent'] / 100)
        max_consecutive = self.settings['max_consecutive_losses']
        
        daily_limit_hit = pnl_today <= -daily_loss_limit
        consecutive_limit_hit = consecutive_losses >= max_consecutive
        
        can_trade = not (daily_limit_hit or consecutive_limit_hit)
        
        # Generate warning
        warning = None
        if daily_limit_hit:
            warning = f"Daily loss limit reached (${abs(pnl_today):.2f}). Stop trading today!"
        elif consecutive_limit_hit:
            warning = f"{consecutive_losses} consecutive losses. Take a break!"
        elif consecutive_losses >= max_consecutive - 1:
            warning = f"Warning: {consecutive_losses} losses in a row. One more = auto-stop"
        elif pnl_today < 0 and abs(pnl_today) > daily_loss_limit * 0.7:
            warning = f"Approaching daily limit (${abs(pnl_today):.2f}/{daily_loss_limit:.2f})"
        
        return {
            'can_trade': can_trade,
            'trades_today': trades_today,
            'pnl_today': round(pnl_today, 2),
            'daily_limit_hit': daily_limit_hit,
            'consecutive_losses': consecutive_losses,
            'warning': warning,
            'wins_today': wins,
            'losses_today': losses
        }
    
    def get_suggestions(self) -> list:
        """Get personalized trading suggestions"""
        suggestions = []
        daily_status = self.check_daily_status()
        
        # Based on current session
        if daily_status['trades_today'] == 0:
            suggestions.append("Start with smaller positions for your first trade of the day")
        
        if daily_status['consecutive_losses'] > 0:
            suggestions.append(f"Take a 15-minute break after {daily_status['consecutive_losses']} losses")
        
        if daily_status['pnl_today'] > self.settings['daily_profit_target']:
            suggestions.append(f"You've hit your daily target (${daily_status['pnl_today']:.2f})! Consider stopping for the day")
        
        # Based on trading style
        style = self.settings['trading_style']
        if style == 'conservative':
            suggestions.append("Wait for 80%+ confidence signals with clear patterns")
        elif style == 'aggressive':
            suggestions.append("Watch for quick scalping opportunities on 1m charts")
        
        return suggestions
    
    def update_settings(self, new_settings: Dict):
        """Update user risk settings"""
        cursor = db.conn.cursor()
        
        # Build update query
        fields = []
        values = []
        
        for key, value in new_settings.items():
            if key in ['account_balance', 'risk_per_trade_percent', 'max_daily_loss_percent',
                      'max_consecutive_losses', 'trading_style', 'daily_profit_target',
                      'monthly_profit_target', 'auto_stop_enabled', 'stop_on_daily_limit',
                      'stop_on_consecutive_losses']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            query = f"UPDATE user_settings SET {', '.join(fields)} WHERE id = 1"
            cursor.execute(query, values)
            db.conn.commit()
            
            # Update local settings cache
            for key, value in new_settings.items():
                if key in self.settings:
                    self.settings[key] = value
            
    def get_current_trade_size(self) -> float:
        """Get position size based on current settings"""
        balance = self.settings['account_balance']
        risk_percent = self.settings['risk_per_trade_percent']
        return round(balance * (risk_percent / 100), 2)
    
    def record_trade_result(self, result: str, profit: float):
        """Update balance after trade result"""
        new_balance = self.settings['account_balance'] + profit
        self.update_settings({'account_balance': round(new_balance, 2)})
        print(f"💰 Balance updated: ${self.settings['account_balance']:.2f} (Profit: {profit:+.2f})")

# Global risk manager instance
risk_manager = RiskManager()
