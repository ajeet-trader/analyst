"""
Asset Tracker - Multi-Asset Watchlist Management
================================================
Tracks performance and stats for each trading asset
"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json

try:
    from dashboard.config import DATABASE
    DB_FILENAME = DATABASE['filename']
except:
    DB_FILENAME = 'signals.db'

from config import CACHE_DIR
DB_PATH = Path(CACHE_DIR).parent / DB_FILENAME


class AssetTracker:
    """Track and manage multi-asset performance"""
    
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def _get_current_session(self) -> str:
        """Determine global market session based on UTC time"""
        hour = datetime.utcnow().hour
        if 0 <= hour < 8:
            return "Asian"
        elif 8 <= hour < 16:
            return "London"
        else:
            return "NY"

    def update_after_signal(self, asset_name: str, signal_id: int, payout_percent: float, confidence: int = 0):
        """Update asset stats after new signal"""
        cursor = self.conn.cursor()
        
        # Get or create asset stats
        cursor.execute("SELECT * FROM asset_stats WHERE asset_name = ?", (asset_name,))
        stats = cursor.fetchone()
        
        if not stats:
            # Create new entry
            conf_hist = json.dumps([confidence]) if confidence > 0 else "[]"
            cursor.execute("""
                INSERT INTO asset_stats (
                    asset_name, total_signals, last_signal_id, last_checked, 
                    current_payout, best_payout, avg_payout, updated_at,
                    confidence_history, session_performance
                ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_name, signal_id, datetime.now().isoformat(),
                payout_percent, payout_percent, payout_percent, 
                datetime.now().isoformat(), conf_hist, "{}"
            ))
        else:
            # Update existing
            total = stats['total_signals'] + 1
            best_payout = max(stats['best_payout'], payout_percent)
            
            # Calculate new average payout
            avg_payout = ((stats['avg_payout'] * stats['total_signals']) + payout_percent) / total
            
            # Update confidence history (keep last 10)
            conf_list = json.loads(stats['confidence_history']) if stats['confidence_history'] else []
            if confidence > 0:
                conf_list.append(confidence)
                if len(conf_list) > 10:
                    conf_list = conf_list[-10:]
            
            cursor.execute("""
                UPDATE asset_stats
                SET total_signals = ?,
                    last_signal_id = ?,
                    last_checked = ?,
                    current_payout = ?,
                    best_payout = ?,
                    avg_payout = ?,
                    updated_at = ?,
                    confidence_history = ?
                WHERE asset_name = ?
            """, (
                total, signal_id, datetime.now().isoformat(),
                payout_percent, best_payout, avg_payout,
                datetime.now().isoformat(), json.dumps(conf_list), asset_name
            ))
        
        self.conn.commit()
    
    def update_after_result(self, asset_name: str, result: str, profit: float):
        """Update asset stats after result is recorded"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM asset_stats WHERE asset_name = ?", (asset_name,))
        stats = cursor.fetchone()
        
        if not stats:
            return  # Should not happen
        
        # Update win/loss counts
        wins = stats['wins'] + (1 if result == 'win' else 0)
        losses = stats['losses'] + (1 if result == 'loss' else 0)
        total_profit = stats['total_profit'] + profit
        
        # Calculate win rate
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        # Update session performance
        session = self._get_current_session()
        session_perf = json.loads(stats['session_performance']) if stats['session_performance'] else {}
        
        if session not in session_perf:
            session_perf[session] = {"wins": 0, "losses": 0, "win_rate": 0}
            
        if result == 'win':
            session_perf[session]["wins"] += 1
        elif result == 'loss':
            session_perf[session]["losses"] += 1
            
        sess_total = session_perf[session]["wins"] + session_perf[session]["losses"]
        session_perf[session]["win_rate"] = (session_perf[session]["wins"] / sess_total * 100) if sess_total > 0 else 0

        # Update streak
        if result in ['win', 'loss']:
            if stats['streak_type'] == result:
                current_streak = stats['current_streak'] + 1
            else:
                current_streak = 1
        else:
            current_streak = 0
            result = None
        
        cursor.execute("""
            UPDATE asset_stats
            SET wins = ?,
                losses = ?,
                win_rate = ?,
                total_profit = ?,
                avg_profit_per_trade = ?,
                current_streak = ?,
                streak_type = ?,
                session_performance = ?,
                updated_at = ?
            WHERE asset_name = ?
        """, (
            wins, losses, win_rate, total_profit, avg_profit,
            current_streak, result, json.dumps(session_perf), 
            datetime.now().isoformat(), asset_name
        ))
        
        self.conn.commit()
    
    def get_asset_stats(self, asset_name: str) -> Optional[Dict]:
        """Get stats for specific asset"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM asset_stats WHERE asset_name = ?", (asset_name,))
        row = cursor.fetchone()
        
        if row:
            stats = dict(row)
            stats['session_performance'] = json.loads(stats['session_performance']) if stats.get('session_performance') else {}
            stats['confidence_history'] = json.loads(stats['confidence_history']) if stats.get('confidence_history') else []
            return stats
        return None
    
    def get_asset_details(self, asset_name: str) -> Optional[Dict]:
        """Get comprehensive details for an asset including trade history"""
        # Get basic stats
        stats = self.get_asset_stats(asset_name)
        if not stats:
            return None
        
        # Get trade history for this asset
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, direction, confidence, payout_percent, expiry, 
                   result, profit, timestamp, reasoning
            FROM signals 
            WHERE asset = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (asset_name,))
        
        trades = []
        for row in cursor.fetchall():
            trade = dict(row)
            trades.append(trade)
        
        # Add trades to stats
        stats['recent_trades'] = trades
        
        return stats
    
    def get_all_assets(self) -> List[Dict]:
        """Get all tracked assets ordered by last checked"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM asset_stats 
            ORDER BY updated_at DESC
        """)
        
        assets = []
        for row in cursor.fetchall():
            asset = dict(row)
            asset['session_performance'] = json.loads(asset['session_performance']) if asset.get('session_performance') else {}
            asset['confidence_history'] = json.loads(asset['confidence_history']) if asset.get('confidence_history') else []
            assets.append(asset)
        
        return assets
    
    def suggest_next_asset(self) -> Optional[Dict]:
        """AI-powered suggestion for next asset to check"""
        cursor = self.conn.cursor()
        
        # Get all assets with scores
        cursor.execute("SELECT * FROM asset_stats")
        assets = [dict(row) for row in cursor.fetchall()]
        
        if not assets:
            return None
        
        now = datetime.now()
        scored_assets = []
        
        for asset in assets:
            score = 0
            
            # Factor 1: Time since last check (40% weight)
            if asset['last_checked']:
                last_check = datetime.fromisoformat(asset['last_checked'])
                hours_since = (now - last_check).total_seconds() / 3600
                time_score = min(hours_since / 2, 10)  # Max 10 points for 2+ hours
                score += time_score * 0.4
            else:
                score += 10 * 0.4  # Never checked = highest priority
            
            # Factor 2: Win rate (30% weight)
            if asset['win_rate'] > 0:
                win_score = asset['win_rate'] / 10  # 70% win rate = 7 points
                score += win_score * 0.3
            
            # Factor 3: Hot streak (20% weight)
            if asset['streak_type'] == 'win' and asset['current_streak'] >= 2:
                streak_score = min(asset['current_streak'], 5)  # Max 5 points
                score += streak_score * 0.2
            
            # Factor 4: Payout (10% weight)
            if asset['current_payout'] > 0:
                payout_score = asset['current_payout'] / 10  # 90% = 9 points
                score += payout_score * 0.1
            
            scored_assets.append({
                'asset': asset,
                'score': score,
                'reasons': []
            })
        
        if not scored_assets:
            return None

        # Get top suggestion
        top = max(scored_assets, key=lambda x: x['score'])
        
        # Build reasons
        asset = top['asset']
        if asset['win_rate'] > 70:
            top['reasons'].append(f"High win rate ({asset['win_rate']:.1f}%)")
        if asset['streak_type'] == 'win' and asset['current_streak'] >= 2:
            top['reasons'].append(f"{asset['current_streak']} win streak")
        if asset['current_payout'] >= 90:
            top['reasons'].append(f"High payout ({asset['current_payout']:.1f}%)")
        
        if asset['last_checked']:
            last_check = datetime.fromisoformat(asset['last_checked'])
            hours = (now - last_check).total_seconds() / 3600
            if hours >= 1:
                top['reasons'].append(f"Not checked in {hours:.1f}h")
        else:
            top['reasons'].append("Never checked")
        
        return {
            'asset_name': asset['asset_name'],
            'score': top['score'],
            'reasons': top['reasons'],
            'stats': asset
        }
    
    def get_heatmap_data(self) -> Dict:
        """Generate performance heatmap data"""
        assets = self.get_all_assets()
        
        heatmap = {}
        for asset in assets:
            # Determine status based on win rate and streak
            if asset['win_rate'] >= 70 and asset['current_streak'] >= 2 and asset['streak_type'] == 'win':
                status = 'hot'
            elif asset['win_rate'] <= 50 or (asset['streak_type'] == 'loss' and asset['current_streak'] >= 2):
                status = 'cold'
            else:
                status = 'neutral'
            
            heatmap[asset['asset_name']] = {
                'win_rate': asset['win_rate'],
                'payout': asset['avg_payout'],
                'status': status,
                'total_signals': asset['total_signals'],
                'streak': f"{asset['current_streak']} {asset['streak_type']}" if asset['streak_type'] else 'none'
            }
        
        return heatmap


# Global instance
asset_tracker = AssetTracker()
