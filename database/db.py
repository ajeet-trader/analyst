"""
Database Connection and Operations
==================================
SQLite database manager
"""
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json

from database.models import Signal, TradeStats
from database.user_settings_model import UserSettings
from config import CACHE_DIR

# Import dashboard config
try:
    from dashboard.config import DATABASE
    DB_FILENAME = DATABASE['filename']
except:
    DB_FILENAME = 'signals.db'

DB_PATH = Path(CACHE_DIR).parent / DB_FILENAME


class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                direction TEXT NOT NULL,
                asset TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                expiry TEXT NOT NULL,
                entry_timing TEXT,
                reasoning TEXT,
                patterns_detected TEXT,
                key_levels TEXT,
                trend_higher_tf TEXT,
                trend_lower_tf TEXT,
                provider_used TEXT,
                analysis_time_ms INTEGER,
                result TEXT,
                user_note TEXT,
                chart_paths TEXT,
                payout_percent REAL DEFAULT 0,
                profit REAL DEFAULT 0
            )
        """)
        
        # Add columns if they don't exist (handle transitions)
        try:
            cursor.execute("ALTER TABLE signals ADD COLUMN payout_percent REAL DEFAULT 0")
        except: pass
        try:
            cursor.execute("ALTER TABLE signals ADD COLUMN profit REAL DEFAULT 0")
        except: pass
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON signals(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset ON signals(asset)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_result ON signals(result)")
        
        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                account_balance REAL DEFAULT 1000.0,
                currency TEXT DEFAULT 'USD',
                risk_per_trade_percent REAL DEFAULT 2.0,
                max_daily_loss_percent REAL DEFAULT 5.0,
                max_consecutive_losses INTEGER DEFAULT 3,
                trading_style TEXT DEFAULT 'conservative',
                daily_profit_target REAL DEFAULT 50.0,
                monthly_profit_target REAL DEFAULT 1000.0,
                auto_stop_enabled INTEGER DEFAULT 1,
                stop_on_daily_limit INTEGER DEFAULT 1,
                stop_on_consecutive_losses INTEGER DEFAULT 1
            )
        """)
        
        # Insert default settings if not exists
        cursor.execute("INSERT OR IGNORE INTO user_settings (id) VALUES (1)")
        
        # Trading sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                
                strategy_name TEXT,
                strategy_snapshot TEXT,
                risk_settings_snapshot TEXT,
                
                total_signals INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                skipped INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0.0,
                
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add session_id column to signals if not exists
        cursor.execute("PRAGMA table_info(signals)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'session_id' not in columns:
            cursor.execute("ALTER TABLE signals ADD COLUMN session_id INTEGER REFERENCES trading_sessions(id)")
        
        # Add payout_percent column if not exists
        if 'payout_percent' not in columns:
            cursor.execute("ALTER TABLE signals ADD COLUMN payout_percent REAL DEFAULT 0")
        
        # Add profit column if not exists (calculated after result)
        if 'profit' not in columns:
            cursor.execute("ALTER TABLE signals ADD COLUMN profit REAL DEFAULT 0")
        
        # Add columns to asset_stats if missing
        cursor.execute("PRAGMA table_info(asset_stats)")
        asset_columns = [col[1] for col in cursor.fetchall()]
        if 'confidence_history' not in asset_columns:
            cursor.execute("ALTER TABLE asset_stats ADD COLUMN confidence_history TEXT")
        
        if 'session_performance' not in asset_columns:
            cursor.execute("ALTER TABLE asset_stats ADD COLUMN session_performance TEXT")
        
        # Journal notes table (general journal entries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                content TEXT NOT NULL,
                tags TEXT,
                mood TEXT,
                session_id INTEGER,
                FOREIGN KEY (session_id) REFERENCES trading_sessions(id) ON DELETE SET NULL
            )
        """)
        
        # Create index for journal notes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_notes(timestamp DESC)")
        
        # Asset stats table (per-asset performance tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name TEXT NOT NULL UNIQUE,
                
                total_signals INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                
                avg_payout REAL DEFAULT 0,
                best_payout REAL DEFAULT 0,
                current_payout REAL DEFAULT 0,
                
                total_profit REAL DEFAULT 0,
                avg_profit_per_trade REAL DEFAULT 0,
                
                last_checked TEXT,
                last_signal_id INTEGER,
                
                current_streak INTEGER DEFAULT 0,
                streak_type TEXT,
                
                session_performance TEXT,
                confidence_history TEXT,  -- JSON: [85, 90, 75, ...]
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (last_signal_id) REFERENCES signals(id)
            )
        """)
        
        # Create index for asset stats
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_name ON asset_stats(asset_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_updated ON asset_stats(updated_at DESC)")
        
        self.conn.commit()
    
    def save_signal(self, signal_data: dict, chart_paths: List[str] = None) -> int:
        """
        Save a new signal to database and link to active session
        
        Returns:
            signal_id
        """
        # Get active session
        session_id = None
        try:
            from sessions import session_manager
            active = session_manager.get_active_session()
            session_id = active['id'] if active else None
        except:
            pass
        
        cursor = self.conn.cursor()
        
        # Convert lists to JSON
        patterns_json = json.dumps(signal_data.get('patterns_detected', []))
        key_levels_json = json.dumps(signal_data.get('key_levels', []))
        charts_json = json.dumps(chart_paths or [])
        
        cursor.execute("""
            INSERT INTO signals (
                direction, asset, confidence, expiry, entry_timing,
                reasoning, patterns_detected, key_levels, trend_higher_tf,
                trend_lower_tf, provider_used, analysis_time_ms, chart_paths, session_id, payout_percent, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_data['direction'],
            signal_data['asset'],
            signal_data['confidence'],
            signal_data['expiry'],
            signal_data.get('entry_timing', ''),
            signal_data.get('reasoning', ''),
            patterns_json,
            key_levels_json,
            signal_data.get('trend_higher_tf', ''),
            signal_data.get('trend_lower_tf', ''),
            signal_data.get('provider', ''),
            signal_data.get('analysis_time_ms', 0),
            charts_json,
            session_id,
            signal_data.get('payout_percent', 0),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_signal_result(self, signal_id: int, result: str, note: str = None):
        """Update signal result (win/loss)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET result = ?, user_note = ?
            WHERE id = ?
        """, (result, note, signal_id))
        self.conn.commit()
        return True
    
    def get_recent_signals(self, limit: int = 20) -> List[dict]:
        """Get recent signals"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM signals 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_stats(self) -> TradeStats:
        """Get aggregated statistics"""
        cursor = self.conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'skip' THEN 1 ELSE 0 END) as skips
            FROM signals
        """)
        row = cursor.fetchone()
        
        if not row:
            return TradeStats(0, 0, 0, 0, 0)
            
        total = row['total'] or 0
        wins = row['wins'] or 0
        losses = row['losses'] or 0
        skips = row['skips'] or 0
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        return TradeStats(
            total_signals=total,
            total_wins=wins,
            total_losses=losses,
            total_skips=skips,
            win_rate=win_rate
        )
    
    def get_trade_note(self, signal_id: int) -> Optional[str]:
        """Get user note for a specific signal"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_note FROM signals WHERE id = ?", (signal_id,))
        row = cursor.fetchone()
        return row['user_note'] if row else None
    
    def save_trade_note(self, signal_id: int, note: str) -> bool:
        """Save or update user note for a signal"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET user_note = ?
            WHERE id = ?
        """, (note, signal_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_trade_note(self, signal_id: int) -> bool:
        """Clear user note for a signal"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET user_note = NULL
            WHERE id = ?
        """, (signal_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global database instance
db = Database()
