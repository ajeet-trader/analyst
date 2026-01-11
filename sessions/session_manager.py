"""
Trading Sessions Manager
=========================
Manage trading sessions with snapshots and analytics
"""
from datetime import datetime
from typing import Dict, List, Optional
import json
from database import db


class SessionManager:
    """Manages trading sessions"""
    
    def __init__(self):
        self.active_session_id = self._get_active_session_id()
    
    def _get_active_session_id(self) -> Optional[int]:
        """Get currently active session ID"""
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id FROM trading_sessions 
            WHERE status = 'active' 
            ORDER BY start_time DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        return row['id'] if row else None
    
    def start_session(self, session_name: str, strategy_name: str, 
                     risk_settings: dict, session_mode: str = 'demo') -> int:
        """
        Start a new trading session
        
        Args:
            session_name: User-defined session name
            strategy_name: Active strategy
            risk_settings: Current risk settings
            session_mode: 'demo' or 'live'
        
        Returns:
            session_id
        """
        # Pause any active sessions first
        if self.active_session_id:
            self.pause_session(self.active_session_id)
        
        cursor = db.conn.cursor()
        
        # Get strategy snapshot
        try:
            from strategies import strategy_engine
            strategy_snapshot = strategy_engine.get_strategy(strategy_name)
        except:
            strategy_snapshot = {}
        
        # Get initial balance from risk settings
        initial_balance = risk_settings.get('account_balance', 0.0)
        
        cursor.execute("""
            INSERT INTO trading_sessions (
                session_name,
                start_time,
                status,
                strategy_name,
                strategy_snapshot,
                risk_settings_snapshot,
                initial_balance,
                session_mode
            ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?)
        """, (
            session_name,
            datetime.now().isoformat(),
            strategy_name,
            json.dumps(strategy_snapshot),
            json.dumps(risk_settings),
            initial_balance,
            session_mode
        ))
        
        db.conn.commit()
        session_id = cursor.lastrowid
        self.active_session_id = session_id
        
        return session_id
    
    def pause_session(self, session_id: int) -> bool:
        """Pause a session"""
        try:
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE trading_sessions 
                SET status = 'paused' 
                WHERE id = ?
            """, (session_id,))
            db.conn.commit()
            
            if session_id == self.active_session_id:
                self.active_session_id = None
            
            return True
        except:
            return False
    
    def resume_session(self, session_id: int) -> bool:
        """Resume a paused session"""
        try:
            # Pause any other active sessions
            if self.active_session_id:
                self.pause_session(self.active_session_id)
            
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE trading_sessions 
                SET status = 'active' 
                WHERE id = ?
            """, (session_id,))
            db.conn.commit()
            
            self.active_session_id = session_id
            return True
        except:
            return False
    
    def end_session(self, session_id: int, notes: str = None) -> bool:
        """End a session"""
        try:
            # Update final stats
            stats = self.get_session_stats(session_id)
            
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE trading_sessions 
                SET status = 'completed',
                    end_time = ?,
                    total_signals = ?,
                    wins = ?,
                    losses = ?,
                    skipped = ?,
                    total_pnl = ?,
                    final_balance = ?,
                    notes = ?
                WHERE id = ?
            """, (
                datetime.now().isoformat(),
                stats['total_signals'],
                stats['wins'],
                stats['losses'],
                stats['skipped'],
                stats['total_pnl'],
                stats['final_balance'],
                notes,
                session_id
            ))
            db.conn.commit()
            
            if session_id == self.active_session_id:
                self.active_session_id = None
            
            return True
        except Exception as e:
            print(f"Error ending session: {e}")
            return False
    
    def get_active_session(self) -> Optional[Dict]:
        """Get current active session"""
        if not self.active_session_id:
            self.active_session_id = self._get_active_session_id()
        
        if not self.active_session_id:
            return None
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM trading_sessions WHERE id = ?
        """, (self.active_session_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_session_stats(self, session_id: int) -> Dict:
        """Get statistics for a session"""
        cursor = db.conn.cursor()
        
        # Get signal stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'skip' THEN 1 ELSE 0 END) as skipped
            FROM signals
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        
        total = row['total'] or 0
        wins = row['wins'] or 0
        losses = row['losses'] or 0
        skipped = row['skipped'] or 0
        
        # Calculate P&L (simplified)
        # Get session's risk settings
        cursor.execute("""
            SELECT risk_settings_snapshot FROM trading_sessions WHERE id = ?
        """, (session_id,))
        session_row = cursor.fetchone()
        
        if session_row:
            risk_settings = json.loads(session_row['risk_settings_snapshot'])
            balance = risk_settings.get('account_balance', 1000)
            risk_percent = risk_settings.get('risk_per_trade_percent', 2)
            risk_per_trade = balance * (risk_percent / 100)
            
            # Assume 80% payout for wins
            pnl = (wins * risk_per_trade * 0.8) - (losses * risk_per_trade)
        else:
            pnl = 0.0
        
        # Get additional info from session row
        cursor.execute("SELECT initial_balance, session_mode FROM trading_sessions WHERE id = ?", (session_id,))
        session_row = cursor.fetchone()
        initial_balance = session_row['initial_balance'] if session_row else 0.0
        session_mode = session_row['session_mode'] if session_row else 'demo'

        return {
            'total_signals': total,
            'wins': wins,
            'losses': losses,
            'skipped': skipped,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'total_pnl': round(pnl, 2),
            'initial_balance': initial_balance,
            'final_balance': round(initial_balance + pnl, 2),
            'session_mode': session_mode
        }
    
    def get_all_sessions(self, limit: int = 50) -> List[Dict]:
        """Get all sessions"""
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM trading_sessions 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            session = dict(row)
            # Add computed stats
            session['stats'] = self.get_session_stats(session['id'])
            sessions.append(session)
        
        return sessions
    
    def get_session_details(self, session_id: int) -> Optional[Dict]:
        """Get detailed session information"""
        cursor = db.conn.cursor()
        
        # Get session
        cursor.execute("SELECT * FROM trading_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        session = dict(row)
        
        # Get all signals in session
        cursor.execute("""
            SELECT * FROM signals 
            WHERE session_id = ? 
            ORDER BY timestamp DESC
        """, (session_id,))
        
        signals = [dict(r) for r in cursor.fetchall()]
        stats = self.get_session_stats(session_id)
        
        # Map field names to match frontend expectations
        return {
            'id': session['id'],
            'name': session.get('session_name', f"Session {session['id']}"),
            'status': session.get('status', 'active'),
            'started_at': session.get('start_time'),
            'ended_at': session.get('end_time'),
            'duration': self._calculate_duration(session.get('start_time'), session.get('end_time')),
            'strategy': session.get('strategy_name'),
            'initial_balance': session.get('initial_balance', 0.0),
            'final_balance': session.get('final_balance') if session.get('status') == 'completed' else stats['final_balance'],
            'session_mode': session.get('session_mode', 'demo'),
            'trades': signals,  # Frontend expects 'trades' not 'signals'
            'stats': stats
        }
    
    def _calculate_duration(self, start_time, end_time):
        """Calculate session duration"""
        if not start_time:
            return "Unknown"
        
        try:
            from datetime import datetime
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else datetime.now()
            
            duration = end - start
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        except:
            return "Ongoing"


# Global session manager
session_manager = SessionManager()
