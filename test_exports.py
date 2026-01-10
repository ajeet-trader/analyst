"""
Test Export Functionality
"""
import sys
sys.path.insert(0, '.')

from database import db
from database.journal_notes_db import JournalNotesDB
from journal.export_manager import export_manager

print("🧪 Testing Export Functionality...\n")

# Get test data
signals = db.get_recent_signals(limit=5)
jndb = JournalNotesDB()

# Create a test note for export
note_id = jndb.create_note(
    title="Market Analysis - January 2026",
    content="Strong bullish momentum on USD pairs. High volatility expected.",
    tags=["market", "analysis"],
    mood="confident"
)

notes = jndb.get_notes(limit=10)

# Test 1: CSV Export
print("📄 Testing CSV Export...")
try:
    csv_buffer = export_manager.export_to_csv(signals)
    csv_content = csv_buffer.read().decode('utf-8')
    lines = csv_content.split('\n')
    print(f"  ✅ Generated CSV with {len(lines)} lines")
    print(f"  Header: {lines[0][:80]}...")
except Exception as e:
    print(f"  ❌ CSV export failed: {e}")

# Test 2: PDF Export
print("\n📕 Testing PDF Export...")
try:
    stats = {
        'total_signals': 10,
        'total_wins': 7,
        'total_losses': 3,
        'win_rate': 70.0
    }
    pdf_buffer = export_manager.export_to_pdf(signals, notes, stats)
    if pdf_buffer:
        pdf_size = len(pdf_buffer.getvalue())
        print(f"  ✅ Generated PDF ({pdf_size} bytes)")
        
        # Save to test file
        with open('cache/test_export.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print(f"  ✅ Saved to cache/test_export.pdf")
    else:
        print(f"  ⚠️ PDF generation returned None (ReportLab might not be installed)")
except Exception as e:
    print(f"  ❌ PDF export failed: {e}")

# Test 3: Trade Card Image
print("\n🖼️ Testing Trade Card Image...")
if signals:
    try:
        signal = signals[0]
        img_buffer = export_manager.generate_trade_card(signal)
        if img_buffer:
            img_size = len(img_buffer.getvalue())
            print(f"  ✅ Generated trade card ({img_size} bytes)")
            
            # Save to test file
            with open('cache/test_trade_card.png', 'wb') as f:
                f.write(img_buffer.getvalue())
            print(f"  ✅ Saved to cache/test_trade_card.png")
        else:
            print(f"  ⚠️ Image generation returned None (Pillow might not be installed)")
    except Exception as e:
        print(f"  ❌ Image export failed: {e}")
else:
    print("  ⚠️ No signals available for testing")

# Cleanup test note
jndb.delete_note(note_id)

print("\n🎉 Export tests complete!")
print("\n📂 Check cache/ folder for generated files:")
print("  - test_export.pdf")
print("  - test_trade_card.png")
