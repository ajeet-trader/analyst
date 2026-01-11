// Session Controls - JavaScript
let activeSession = null;

document.addEventListener('DOMContentLoaded', () => {
    loadActiveSession();
    setInterval(loadActiveSession, 5000); // Refresh every 5s
});

async function loadActiveSession() {
    try {
        const res = await fetch('/api/sessions/active');
        const session = await res.json();

        if (session && session.id) {
            activeSession = session;
            updateSessionDisplay();
        } else {
            activeSession = null;
            updateSessionDisplay();
        }
    } catch (err) {
        console.error('Failed to load active session:', err);
    }
}

function updateSessionDisplay() {
    const widget = document.getElementById('session-widget');
    if (!widget) return;

    if (activeSession) {
        const stats = activeSession.stats || { total_signals: 0, wins: 0, losses: 0, total_pnl: 0 };
        const duration = calculateDuration(activeSession.start_time);

        widget.innerHTML = `
            <div class="session-active">
                <div class="session-info">
                    <div class="session-name">${activeSession.session_name}</div>
                    <div class="session-meta">
                        <span>${duration}</span> • 
                        <span>${stats.total_signals} trades</span> • 
                        <span class="${stats.total_pnl >= 0 ? 'profit' : 'loss'}">$${stats.total_pnl.toFixed(2)}</span>
                    </div>
                </div>
                <div class="session-actions">
                    <button onclick="pauseSession()" class="btn-session-pause">⏸ Pause</button>
                    <button onclick="showEndSessionModal()" class="btn-session-end">⏹ End</button>
                </div>
            </div>
        `;
    } else {
        widget.innerHTML = `
            <div class="session-inactive">
                <p>No active session</p>
                <button onclick="showStartSessionModal()" class="btn-session-start">▶ Start Session</button>
            </div>
        `;
    }
}

function calculateDuration(startTime) {
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000); // seconds

    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

function showStartSessionModal() {
    // Check if strategy and risk are configured first
    fetch('/api/risk/settings')
        .then(res => res.json())
        .then(riskSettings => {
            const balance = riskSettings.account_balance || 0;
            const riskPercent = riskSettings.risk_per_trade_percent || 0;

            if (balance === 0 || riskPercent === 0) {
                if (confirm('⚠️ Risk settings not configured!\n\nWould you like to set up your risk settings first?')) {
                    window.location.href = '/risk';
                    return;
                }
            }

            // Show modal
            const modal = document.getElementById('start-session-modal');
            if (modal) {
                modal.style.display = 'flex';
                // Reset fields
                document.getElementById('modal-session-name').value = '';
                document.querySelector('input[name="session-mode"][value="demo"]').checked = true;
                document.getElementById('modal-market-type').value = 'binary';
                updateModeStyle();
            }
        });
}

function closeStartSessionModal() {
    const modal = document.getElementById('start-session-modal');
    if (modal) modal.style.display = 'none';
}

function updateModeStyle() {
    const isLive = document.querySelector('input[name="session-mode"][value="live"]').checked;
    const warning = document.getElementById('live-warning');
    if (warning) warning.style.display = isLive ? 'block' : 'none';
}

async function startNewSession() {
    const nameInput = document.getElementById('modal-session-name');
    const modeInput = document.querySelector('input[name="session-mode"]:checked');
    const marketInput = document.getElementById('modal-market-type');

    const sessionName = nameInput.value.trim() || `Session ${new Date().toLocaleString()}`;
    const mode = modeInput.value;
    const marketType = marketInput.value;

    if (mode === 'live') {
        if (!confirm('⚠️ CONFIRM LIVE TRADING\n\nYou are about to start a LIVE trading session.\nEnsure your broker is connected and you are ready to trade real funds.\n\nProceed?')) {
            return;
        }
    }

    try {
        const res = await fetch('/api/sessions/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_name: sessionName,
                mode: mode,
                market_type: marketType
            })
        });

        const data = await res.json();
        if (data.success) {
            closeStartSessionModal();
            // alert(`✅ ${mode.toUpperCase()} Session Started!`);
            loadActiveSession();
        }
    } catch (err) {
        console.error('Failed to start session:', err);
        alert('❌ Failed to start session');
    }
}

async function pauseSession() {
    if (!activeSession) return;

    try {
        const res = await fetch(`/api/sessions/${activeSession.id}/pause`, {
            method: 'POST'
        });

        const data = await res.json();
        if (data.success) {
            alert('⏸ Session paused');
            loadActiveSession();
        }
    } catch (err) {
        console.error('Failed to pause session:', err);
    }
}

function showEndSessionModal() {
    const notes = prompt('Session Notes (optional - what did you learn?):');
    endSession(notes || '');
}

async function endSession(notes) {
    if (!activeSession) return;

    if (!confirm(`End session "${activeSession.session_name}"?`)) {
        return;
    }

    try {
        const res = await fetch(`/api/sessions/${activeSession.id}/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes })
        });

        const data = await res.json();
        if (data.success) {
            alert('⏹ Session ended! View in Sessions History.');
            loadActiveSession();
        }
    } catch (err) {
        console.error('Failed to end session:', err);
    }
}
