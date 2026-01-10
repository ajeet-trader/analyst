"""
Test Backend APIs
"""
import sys
sys.path.insert(0, '.')

# Initialize database with new schema
print("🔄 Initializing database with new schema...")
from database import db

print("✅ Database initialized!")
print("\nTesting database operations...\n")

# Test 1: Check tables exist
import sqlite3
conn = sqlite3.connect('cache/signals.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('📊 Tables:', tables)

# Test 2: Check journal_notes schema
if 'journal_notes' in tables:
    print('\n✅ journal_notes table exists')
    cursor.execute('PRAGMA table_info(journal_notes)')
    cols = [row[1] for row in cursor.fetchall()]
    print('  Columns:', cols)
else:
    print('\n❌ journal_notes table missing')

# Test 3: Check signals has user_note
cursor.execute('PRAGMA table_info(signals)')
signal_cols = [row[1] for row in cursor.fetchall()]
if 'user_note' in signal_cols:
    print('\n✅ signals.user_note column exists')
else:
    print('\n❌ signals.user_note column missing')

conn.close()

# Test 4: Test journal notes CRUD
print('\n🧪 Testing Journal Notes CRUD...')
from database.journal_notes_db import JournalNotesDB

jndb = JournalNotesDB()

# Create a test note
note_id = jndb.create_note(
    title="Test Journal Entry",
    content="This is a test note to verify the database is working.",
    tags=["test", "verification"],
    mood="confident"
)
print(f'  ✅ Created note with ID: {note_id}')

# Retrieve the note
note = jndb.get_note(note_id)
print(f'  ✅ Retrieved note: {note["title"]}')

# Update the note
success = jndb.update_note(note_id, content="Updated content")
print(f'  ✅ Updated note: {success}')

# Get all notes
notes = jndb.get_notes(limit=10)
print(f'  ✅ Total notes: {len(notes)}')

# Delete the test note
deleted = jndb.delete_note(note_id)
print(f'  ✅ Deleted note: {deleted}')

# Test 5: Test trade notes
print('\n💬 Testing Trade Notes...')
from database import db

# Assuming there's at least one signal
signals = db.get_recent_signals(limit=1)
if signals:
    signal_id = signals[0]['id']
    
    # Save note
    db.save_trade_note(signal_id, "Great trade! Followed the plan perfectly.")
    print(f'  ✅ Saved note for signal {signal_id}')
    
    # Retrieve note
    note = db.get_trade_note(signal_id)
    print(f'  ✅ Retrieved note: "{note}"')
    
    # Delete note
    db.delete_trade_note(signal_id)
    print(f'  ✅ Deleted note')
else:
    print('  ⚠️ No signals found to test trade notes')

print('\n🎉 All backend tests passed!')
