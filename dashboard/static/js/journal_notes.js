// Journal Notes Management
// Handles trade notes and general journal entries

// ==================
// TRADE NOTES
// ==================

// Show note modal after recording result
window.showTradeNoteModal = function (signalId) {
    const modal = createNoteModal(signalId);
    document.body.appendChild(modal);

    // Load template
    fetch('/api/journal/templates/trade')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('note-content').value = data.template;
            }
        });
};

function createNoteModal(signalId) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'note-modal';

    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>📝 Add Trade Note (Optional)</h3>
                <button class="modal-close" onclick="closeNoteModal()">&times;</button>
            </div>
            <div class="modal-body">
                <textarea id="note-content" rows="12" placeholder="Add your notes here..."></textarea>
            </div>
            <div class="modal-footer" style="display: flex; justify-content: space-between;">
                <button class="btn-skip" onclick="closeNoteModal()" 
                    style="padding: 10px 24px; background: transparent; color: #9ca3b8; border: 1px solid #2d3a5f; border-radius: 8px; cursor: pointer; font-weight: 600;">⏩ Skip & Record</button>
                <button class="btn-primary" onclick="saveTradeNote(${signalId})">Save Note</button>
            </div>
        </div>
    `;

    return modal;
}

window.closeNoteModal = function () {
    const modal = document.getElementById('note-modal');
    if (modal) {
        modal.remove();
    }
};

window.saveTradeNote = async function (signalId) {
    const content = document.getElementById('note-content').value.trim();

    if (!content) {
        closeNoteModal();
        return;
    }

    try {
        const res = await fetch(`/api/signals/${signalId}/note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note: content })
        });

        const data = await res.json();
        if (data.success) {
            showNotification('✅ Note saved!', 'success');
            closeNoteModal();
            refreshJournal();
        }
    } catch (err) {
        console.error('Failed to save note:', err);
        showNotification('❌ Failed to save note', 'error');
    }
};

// Utility to refresh journal if on journal page/dashboard
function refreshJournal() {
    if (typeof loadJournal === 'function') loadJournal();
    if (typeof loadGeneralNotes === 'function') loadGeneralNotes();
    if (typeof loadRecentHistory === 'function') loadRecentHistory();
}

// ==================
// GENERAL JOURNAL
// ==================

window.showJournalEntryModal = function () {
    const modal = createJournalModal();
    document.body.appendChild(modal);

    // Load template
    fetch('/api/journal/templates/general')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('journal-content').value = data.template;
            }
        });
};

function createJournalModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'journal-modal';

    modal.innerHTML = `
        <div class="modal-container large">
            <div class="modal-header">
                <h3>📔 New Journal Entry</h3>
                <button class="modal-close" onclick="closeJournalModal()">&times;</button>
            </div>
            <div class="modal-body">
                <input type="text" id="journal-title" placeholder="Entry Title (optional)" class="form-input" />
                <textarea id="journal-content" rows="15" placeholder="Write your journal entry..."></textarea>
                
                <div class="journal-meta">
                    <div class="form-group">
                        <label>Tags (comma separated)</label>
                        <input type="text" id="journal-tags" placeholder="psychology, market, technical" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Mood</label>
                        <select id="journal-mood" class="form-input">
                            <option value="">Select mood...</option>
                            <option value="confident">😎 Confident</option>
                            <option value="uncertain">😐 Uncertain</option>
                            <option value="frustrated">😤 Frustrated</option>
                            <option value="motivated">🔥 Motivated</option>
                            <option value="calm">😌 Calm</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeJournalModal()">Cancel</button>
                <button class="btn-primary" onclick="saveJournalEntry()">Save Entry</button>
            </div>
        </div>
    `;

    return modal;
}

window.closeJournalModal = function () {
    const modal = document.getElementById('journal-modal');
    if (modal) {
        modal.remove();
    }
};

window.saveJournalEntry = async function () {
    const title = document.getElementById('journal-title').value.trim();
    const content = document.getElementById('journal-content').value.trim();
    const tagsStr = document.getElementById('journal-tags').value.trim();
    const mood = document.getElementById('journal-mood').value;

    if (!content) {
        showNotification('❌ Content is required', 'error');
        return;
    }

    const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : [];

    try {
        const res = await fetch('/api/journal/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title || null,
                content,
                tags,
                mood: mood || null
            })
        });

        const data = await res.json();
        if (data.success) {
            showNotification('✅ Journal entry saved!', 'success');
            closeJournalModal();

            // Reload journal if we're on that page
            if (typeof loadJournalNotes === 'function') {
                loadJournalNotes();
            }
        }
    } catch (err) {
        console.error('Failed to save journal entry:', err);
        showNotification('❌ Failed to save entry', 'error');
    }
};

// ==================
// EXPORT
// ==================

window.showExportModal = function () {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'export-modal';

    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>📤 Export Journal</h3>
                <button class="modal-close" onclick="closeExportModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="export-options">
                    <div class="export-option" onclick="exportToPDF()">
                        <div class="export-icon">📕</div>
                        <h4>PDF Report</h4>
                        <p>Complete journal with stats, signals, and notes</p>
                    </div>
                    <div class="export-option" onclick="exportToCSV()">
                        <div class="export-icon">📊</div>
                        <h4>CSV Data</h4>
                        <p>Spreadsheet format for analysis</p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeExportModal()">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
};

window.closeExportModal = function () {
    const modal = document.getElementById('export-modal');
    if (modal) {
        modal.remove();
    }
};

window.exportToPDF = function () {
    showNotification('📕 Generating PDF...', 'info');
    window.location.href = '/api/journal/export/pdf';
    setTimeout(() => {
        showNotification('✅ PDF downloaded!', 'success');
        closeExportModal();
    }, 1000);
};

window.exportToCSV = function () {
    showNotification('📊 Generating CSV...', 'info');
    window.location.href = '/api/journal/export/csv';
    setTimeout(() => {
        showNotification('✅ CSV downloaded!', 'success');
        closeExportModal();
    }, 1000);
};

window.exportTradeCard = function (signalId) {
    showNotification('🖼️ Generating trade card...', 'info');
    window.location.href = `/api/journal/export/image/${signalId}`;
    setTimeout(() => {
        showNotification('✅ Trade card downloaded!', 'success');
    }, 1000);
};

// ==================
// HELPERS
// ==================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
