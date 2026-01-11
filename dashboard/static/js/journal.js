// Journal Page - Display archived trades
document.addEventListener('DOMContentLoaded', () => {
    loadJournal();
    loadGeneralNotes();
});

let currentTab = 'all';

function switchTab(tab) {
    currentTab = tab;

    // Update UI
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.innerText.toLowerCase().includes(tab)) btn.classList.add('active');
    });

    // Hacky mapping since button text differs from 'rejected'
    if (tab === 'all') {
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.remove('active');
    } else {
        document.querySelectorAll('.tab-btn')[0].classList.remove('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }

    loadJournal();
}

async function loadJournal() {
    try {
        const mode = document.getElementById('filter-mode').value;
        const market = document.getElementById('filter-market').value;

        let url = `/api/journal/recent?limit=50&mode=${mode}&market=${market}`;

        if (currentTab === 'rejected') {
            url = `/api/signals/skipped?limit=50&mode=${mode}&market=${market}`;
        }

        const res = await fetch(url);
        const trades = await res.json();

        displayJournal(trades);
    } catch (err) {
        console.error('Failed to load journal:', err);
    }
}

async function loadGeneralNotes() {
    try {
        const res = await fetch('/api/journal/notes?limit=20');
        const data = await res.json();
        if (data.success) {
            displayGeneralNotes(data.notes);
        }
    } catch (err) {
        console.error('Failed to load general notes:', err);
    }
}

function displayGeneralNotes(notes) {
    const container = document.getElementById('notes-list');
    if (!container) return;

    if (!notes || notes.length === 0) {
        container.innerHTML = '<p class="empty-state">No personal notes yet</p>';
        return;
    }

    container.innerHTML = notes.map(note => {
        const date = new Date(note.timestamp).toLocaleDateString();
        const moodEmoji = {
            'confident': '😎',
            'uncertain': '😐',
            'frustrated': '😤',
            'motivated': '🔥',
            'calm': '😌'
        }[note.mood] || '📝';

        return `
            <div class="note-item">
                <div class="note-header">
                    <span class="note-mood">${moodEmoji}</span>
                    <strong class="note-title">${note.title || 'Untitled Note'}</strong>
                </div>
                <div class="note-content">${note.content.substring(0, 100)}${note.content.length > 100 ? '...' : ''}</div>
                <div class="note-footer">
                    <span class="note-date">${date}</span>
                    <div class="note-tags">
                        ${note.tags ? note.tags.map(t => `<span class="tag-badge">${t}</span>`).join('') : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function displayJournal(trades) {
    const container = document.getElementById('journal-list');

    if (!trades || trades.length === 0) {
        container.innerHTML = '<p class="empty-state">No trades journaled yet</p>';
        return;
    }

    container.innerHTML = trades.map(trade => {
        const timestamp = new Date(trade.timestamp).toLocaleString();
        const result = trade.result || 'pending';
        const resultClass = result === 'win' ? 'win' : result === 'loss' ? 'loss' : 'pending';
        const resultIcon = result === 'win' ? '✅' : result === 'loss' ? '❌' : '⏳';

        const suggestions = trade.post_analysis?.suggestions || [];

        // Determine market icon
        const marketIcons = { 'binary': '📊', 'forex': '💱', 'crypto': '₿', 'stock': '📈' };
        const marketIcon = marketIcons[trade.market_type] || '📊';

        // Determine mode badge
        const isLive = trade.mode === 'live';
        const modeBadge = isLive
            ? `<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 2px 8px; border-radius: 4px; font-size: 11px;">🟢 LIVE</span>`
            : `<span style="background: rgba(59, 130, 246, 0.2); color: #3b82f6; padding: 2px 8px; border-radius: 4px; font-size: 11px;">🔵 DEMO</span>`;

        // Signal ID might be id or signal_id depending on source
        const signalId = trade.id || trade.signal_id;

        return `
            <div class="journal-entry ${resultClass}">
                <div class="journal-header">
                    <div class="journal-title">
                        <span class="journal-result-icon">${resultIcon}</span>
                        <span class="journal-direction ${trade.direction.toLowerCase()}">${trade.direction}</span>
                        <span class="journal-asset">${trade.asset}</span>
                        <span style="font-size: 14px; margin-left: 10px;" title="${trade.market_type}">${marketIcon}</span>
                    </div>
                    <div class="journal-meta">
                        ${modeBadge}
                        <span class="journal-time">${timestamp}</span>
                        <span class="journal-confidence">${trade.confidence}%</span>
                        <button class="btn-modify" onclick="modifyResult(${signalId})">✏️ Modify</button>
                    </div>
                </div>
                
                <div class="journal-details">
                    <div class="journal-info">
                        <strong>Payout:</strong> <span style="color: var(--accent-blue)">${trade.payout_percent || 0}%</span> |
                        <strong>Expiry:</strong> ${trade.expiry} | 
                        <strong>Timing:</strong> ${trade.entry_timing || 'N/A'} |
                        <strong>Provider:</strong> ${trade.provider || 'N/A'}
                    </div>
                    
                    ${trade.patterns_detected && trade.patterns_detected.length > 0 ? `
                        <div class="journal-patterns">
                            <strong>Patterns:</strong> 
                            ${trade.patterns_detected.map(p => `<span class="pattern-badge">${p.replace(/_/g, ' ')}</span>`).join(' ')}
                        </div>
                    ` : ''}
                    
                    <div class="journal-reasoning">
                        <strong>💡 Reasoning:</strong> ${trade.reasoning || 'No reasoning provided'}
                    </div>
                    
                    ${trade.user_note ? `
                        <div class="journal-note">
                            <strong>📝 Note:</strong> ${trade.user_note}
                        </div>
                    ` : ''}
                    
                    ${suggestions.length > 0 ? `
                        <div class="journal-suggestions">
                            <strong>💭 Suggestions:</strong>
                            <ul>
                                ${suggestions.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="journal-charts">
                        ${trade.charts && trade.charts.length > 0 ?
                trade.charts.map((chart, i) =>
                    `<div class="journal-chart-thumb">
                                    <img src="/archive/${chart.split('archives/')[1] || chart}" alt="Chart ${i + 1}" />
                                </div>`
                ).join('')
                : '<p class="empty-state">No charts archived</p>'
            }
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

window.modifyResult = async function (signalId) {
    const result = prompt("Enter manual result (win, loss, or draw):", "win");
    if (!result) return;

    if (!['win', 'loss', 'draw'].includes(result.toLowerCase())) {
        alert("Invalid result! Please use 'win', 'loss', or 'draw'.");
        return;
    }

    try {
        const res = await fetch(`/api/signals/${signalId}/modify_result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ result: result.toLowerCase() })
        });

        const data = await res.json();
        if (data.success) {
            alert("✅ Result modified successfully!");
            loadJournal(); // Refresh
        } else {
            alert("❌ Failed to modify result: " + data.error);
        }
    } catch (err) {
        console.error('Failed to modify result:', err);
    }
}
