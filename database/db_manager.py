"""
Database Management Utilities
==============================
Tools for managing database: reset, delete trades, cleanup
"""
from database import db
from pathlib import Path
import shutil
from datetime import datetime


class DatabaseManager:
    """Manage database operations"""
    
    def reset_database(self, confirm: bool = False) -> dict:
        """
        Reset entire database (DELETE ALL DATA)
        
        Args:
            confirm: Must be True to actually reset
        """
        if not confirm:
            return {'success': False, 'error': 'Confirmation required'}
        
        try:
            cursor = db.conn.cursor()
            
            # Delete all signals and sessions
            cursor.execute('DELETE FROM signals')
            cursor.execute('DELETE FROM trading_sessions')
            
            # Reset user settings to defaults
            cursor.execute('UPDATE user_settings SET account_balance = 1000.0 WHERE id = 1')
            
            db.conn.commit()
            
            # Also clear journal archives
            from journal.journal_manager import ARCHIVES_DIR
            if ARCHIVES_DIR.exists():
                for trade_dir in ARCHIVES_DIR.glob('trade_*'):
                    shutil.rmtree(trade_dir)
            
            return {'success': True, 'message': 'Database reset successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_signal(self, signal_id: int) -> dict:
        """Delete a specific signal and its journal entry"""
        try:
            cursor = db.conn.cursor()
            
            # Delete from database
            cursor.execute('DELETE FROM signals WHERE id = ?', (signal_id,))
            db.conn.commit()
            
            # Delete journal archive
            from journal.journal_manager import ARCHIVES_DIR
            trade_dirs = list(ARCHIVES_DIR.glob(f'trade_{signal_id}_*'))
            for trade_dir in trade_dirs:
                shutil.rmtree(trade_dir)
            
            return {'success': True, 'message': f'Signal {signal_id} deleted'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_data(self, days: int = 90) -> dict:
        """Delete signals older than specified days"""
        try:
            cursor = db.conn.cursor()
            
            cursor.execute("""
                DELETE FROM signals 
                WHERE DATE(timestamp) < DATE('now', ? || ' days')
            """, (f'-{days}',))
            
            deleted = cursor.rowcount
            db.conn.commit()
            
            return {'success': True, 'deleted': deleted}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            cursor = db.conn.cursor()
            
            # Total signals
            cursor.execute('SELECT COUNT(*) FROM signals')
            total_signals = cursor.fetchone()[0]
            
            # Signals with results
            cursor.execute('SELECT COUNT(*) FROM signals WHERE result IS NOT NULL')
            completed_trades = cursor.fetchone()[0]
            
            # Database size
            from database.db import DB_PATH
            db_size_mb = DB_PATH.stat().st_size / (1024 * 1024) if DB_PATH.exists() else 0
            
            # Journal size
            from journal.journal_manager import ARCHIVES_DIR
            journal_size_mb = sum(
                f.stat().st_size for f in ARCHIVES_DIR.rglob('*') if f.is_file()
            ) / (1024 * 1024) if ARCHIVES_DIR.exists() else 0
            
            return {
                'total_signals': total_signals,
                'completed_trades': completed_trades,
                'pending_trades': total_signals - completed_trades,
                'database_size_mb': round(db_size_mb, 2),
                'journal_size_mb': round(journal_size_mb, 2),
                'total_size_mb': round(db_size_mb + journal_size_mb, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}


# Global database manager
db_manager = DatabaseManager()
