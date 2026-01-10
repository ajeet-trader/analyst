import sqlite3
from pathlib import Path

# Connect to database
db_path = Path('cache/signals.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('✅ Database Tables:')
for table in tables:
    print(f'  - {table}')

# Check journal_notes schema
print('\n📝 journal_notes columns:')
cursor.execute('PRAGMA table_info(journal_notes)')
for row in cursor.fetchall():
    print(f'  - {row[1]} ({row[2]})')

# Check if signals table has user_note column
print('\n💬 signals table user_note column:')
cursor.execute('PRAGMA table_info(signals)')
cols = [row[1] for row in cursor.fetchall()]
if 'user_note' in cols:
    print('  ✅ user_note column exists')
else:
    print('  ❌ user_note column missing')

conn.close()
print('\n✅ Database schema verification complete!')
