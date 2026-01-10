"""
Journal Notes Database Operations
==================================
Handle CRUD operations for general journal notes
"""
import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
import json
from pathlib import Path

try:
    from dashboard.config import DATABASE
    DB_FILENAME = DATABASE['filename']
except:
    DB_FILENAME = 'signals.db'

from config import CACHE_DIR
DB_PATH = Path(CACHE_DIR).parent / DB_FILENAME


class JournalNotesDB:
    """Database operations for journal notes"""
    
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def create_note(self, title: Optional[str], content: str, tags: Optional[List[str]] = None, 
                   mood: Optional[str] = None, session_id: Optional[int] = None) -> int:
        """Create a new journal note"""
        cursor = self.conn.cursor()
        tags_json = json.dumps(tags) if tags else None
        
        cursor.execute("""
            INSERT INTO journal_notes (title, content, tags, mood, session_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, content, tags_json, mood, session_id, datetime.now().isoformat()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_notes(self, limit: int = 50, offset: int = 0, session_id: Optional[int] = None) -> List[Dict]:
        """Get journal notes with pagination"""
        cursor = self.conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT * FROM journal_notes 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (session_id, limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM journal_notes 
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        
        rows = cursor.fetchall()
        notes = []
        for row in rows:
            note = dict(row)
            if note['tags']:
                note['tags'] = json.loads(note['tags'])
            notes.append(note)
        
        return notes
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Get a specific journal note"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM journal_notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        
        if row:
            note = dict(row)
            if note['tags']:
                note['tags'] = json.loads(note['tags'])
            return note
        return None
    
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None,
                   tags: Optional[List[str]] = None, mood: Optional[str] = None) -> bool:
        """Update a journal note"""
        cursor = self.conn.cursor()
        
        # Build dynamic update query based on provided fields
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        if mood is not None:
            updates.append("mood = ?")
            params.append(mood)
        
        if not updates:
            return False
        
        params.append(note_id)
        query = f"UPDATE journal_notes SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a journal note"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM journal_notes WHERE id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_note_count(self, session_id: Optional[int] = None) -> int:
        """Get total count of notes"""
        cursor = self.conn.cursor()
        
        if session_id:
            cursor.execute("SELECT COUNT(*) FROM journal_notes WHERE session_id = ?", (session_id,))
        else:
            cursor.execute("SELECT COUNT(*) FROM journal_notes")
        
        return cursor.fetchone()[0]
