// AI Trading Assistant Dashboard - Real-time updates
const socket = io();

// State
let currentSignal = null;
let timerInterval = null;

// Connect to WebSocket
socket.on('connect', () => {
    console.log('Connected to dashboard');
});

socket.on('state_update', (state) => {
    updateStatus(state.status);
    updateCaptures(state.captures);
    updateStats(state.stats);
    if (state.current_signal) {
        displaySignal(state.current_signal);
    } else {
        // Clear signal display if no active signal
        const display = document.getElementById('signal-display');
        if (display && !display.querySelector('.waiting-state')) {
            display.innerHTML = '<div class="waiting-state"><div class="signal-icon-placeholder">📊</div><h3>WAITING FOR SIGNAL</h3><p>Press \'aa\' to capture charts, then \'c\' to analyze</p></div>';
            document.getElementById('quick-actions').style.display = 'none';
            currentSignal = null;
        }
    }
    if (state.signal_history && state.signal_history.length > 0) {
        updateHistory(state.signal_history);
    }
});

// Status updates
socket.on('status_update', (data) => {
    updateStatus(data.status);
});

// Captures updates
socket.on('captures_update', (data) => {
    updateCaptures(data.captures);
    document.getElementById('capture-count').textContent = data.count;
});

// Signal updates
socket.on('signal_update', (data) => {
    displaySignal(data.signal);
    playNotificationSound();
});

// History updates
socket.on('history_update', (data) => {
    updateHistory(data.history);
});

// Error updates
socket.on('error_update', (data) => {
    displayError(data.error);
});

// Stats updates
socket.on('stats_update', (stats) => {
    updateStats(stats);
});

// Update functions
function updateStatus(status) {
    document.getElementById('status-text').textContent = status;
    const dot = document.getElementById('status-dot');

    if (status.toLowerCase().includes('analyzing')) {
        dot.style.background = '#f59e0b';
    } else if (status.toLowerCase().includes('error')) {
        dot.style.background = '#ef4444';
    } else {
        dot.style.background = '#10b981';
    }
}

function updateCaptures(captures) {
    const grid = document.getElementById('captures-grid');

    if (!captures || captures.length === 0) {
        grid.innerHTML = '<p class="empty-state">No captures yet</p>';
        return;
    }

    grid.innerHTML = captures.map((capture, i) => {
        // Extract filename from path
        const filename = capture.path.split(/[\\/]/).pop();
        return `
        <div class="capture-thumb">
            <img src="/cache/${filename}" alt="Capture ${i + 1}" onerror="this.style.display='none'" />
        </div>
    `;
    }).join('');
}

function displaySignal(signal) {
    currentSignal = signal;
    const display = document.getElementById('signal-display');

    const isCall = signal.direction === 'CALL';
    const isPut = signal.direction === 'PUT';
    const color = isCall ? 'var(--accent-green)' : isPut ? 'var(--accent-red)' : 'var(--text-secondary)';
    const arrow = isCall ? '▲' : isPut ? '▼' : '●';

    display.innerHTML = `
        <div class="signal-active">
            <div class="signal-direction">
                <span class="signal-arrow" style="color: ${color}">${arrow}</span>
                <span class="signal-text signal-${signal.direction.toLowerCase()}">${signal.direction}</span>
            </div>
            
            <div class="signal-asset">${signal.asset || 'Unknown Asset'}</div>
            <div class="signal-expiry">⏱ EXPIRY: ${signal.expiry.toUpperCase()}</div>
            
            <div class="signal-stats">
                <div class="signal-stat">
                    <div class="signal-stat-label">CONFIDENCE</div>
                    <div class="confidence-ring" style="border-color: ${color}">
                        <span style="color: ${color}">${signal.confidence}%</span>
                    </div>
                </div>
                <div class="signal-stat">
                    <div class="signal-stat-label">COUNTDOWN</div>
                    <div class="countdown" id="countdown">--:--</div>
                </div>
            </div>
            
            ${signal.patterns_detected && signal.patterns_detected.length > 0 ? `
                <div class="patterns-badges">
                    ${signal.patterns_detected.map(p => `
                        <span class="pattern-badge">${p.replace(/_/g, ' ').toUpperCase()}</span>
                    `).join('')}
                </div>
            ` : ''}
            
            ${signal.reasoning ? `
                <div class="signal-reasoning">
                    <h4>💡 WHY THIS TRADE</h4>
                    <p>${signal.reasoning}</p>
                    ${signal.key_levels ? `<p>📍 Key levels: ${signal.key_levels.join(', ')}</p>` : ''}
                    ${signal.entry_timing ? `<p>▶ ${formatEntryTiming(signal.entry_timing)}</p>` : ''}
                </div>
            ` : ''}
        </div>
    `;

    // Show quick actions
    document.getElementById('quick-actions').style.display = 'flex';

    // Start countdown
    startCountdown(signal.expiry, signal.timestamp);
}

function displayError(error) {
    const display = document.getElementById('signal-display');
    display.innerHTML = `
        <div class="signal-active error">
            <div class="signal-direction">
                <span class="signal-text">ERROR</span>
            </div>
            <div class="signal-reasoning">
                <h4>Analysis Failed</h4>
                <p>${error}</p>
                <p style="margin-top: 10px; color: var(--accent-blue);">
                    Images kept in cache. Press 'v' to view, 'c' to retry.
                </p>
            </div>
        </div>
    `;
}

function startCountdown(expiry, timestamp) {
    if (timerInterval) clearInterval(timerInterval);

    // Calculate initial remaining time from timestamp
    // Robust parsing for Local ISO timestamp
    const parseISO = (str) => {
        if (!str) return new Date();
        const t = str.includes('T') ? str : str.replace(' ', 'T');
        return new Date(t);
    };

    const expiryMinutes = parseExpiryToMinutes(expiry);
    const signalTime = parseISO(timestamp);
    const expiryTime = new Date(signalTime.getTime() + expiryMinutes * 60000);

    const countdown = document.getElementById('countdown');

    timerInterval = setInterval(() => {
        const now = new Date();
        const secondsRemaining = Math.floor((expiryTime - now) / 1000);

        if (secondsRemaining <= 0) {
            clearInterval(timerInterval);
            if (countdown) {
                countdown.textContent = 'EXPIRED';
                countdown.classList.add('warning');
            }
            return;
        }

        if (countdown) {
            const mins = Math.floor(secondsRemaining / 60);
            const secs = secondsRemaining % 60;
            countdown.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

            if (secondsRemaining <= 10) {
                countdown.classList.add('warning');
            } else {
                countdown.classList.remove('warning');
            }
        }
    }, 1000);
}

function parseExpiryToMinutes(expiry) {
    if (!expiry) return 1;
    const exp = expiry.toLowerCase();
    if (exp.endsWith('s')) return parseInt(exp) / 60;
    if (exp.endsWith('h')) return parseInt(exp) * 60;
    return parseInt(exp) || 1;
}

function formatEntryTiming(timing) {
    const map = {
        'now': 'Enter immediately',
        'candle_close': 'Wait for current candle to close',
        'wait_pullback': 'Wait for a pullback before entry'
    };
    return map[timing] || timing;
}

function updateStats(stats) {
    document.getElementById('wins').textContent = stats.wins || 0;
    document.getElementById('losses').textContent = stats.losses || 0;

    const total = (stats.wins || 0) + (stats.losses || 0);
    const winrate = total > 0 ? ((stats.wins || 0) / total * 100).toFixed(0) : 0;
    document.getElementById('winrate').textContent = `${winrate}%`;
}

function updateHistory(history) {
    const list = document.getElementById('history-list');

    if (!history || history.length === 0) {
        list.innerHTML = '<p class="empty-state">No signals yet</p>';
        return;
    }

    list.innerHTML = history.map(signal => {
        const parseISO = (str) => {
            if (!str) return new Date();
            const t = str.includes('T') ? str : str.replace(' ', 'T');
            return new Date(t);
        };
        const time = signal.timestamp ? parseISO(signal.timestamp).toLocaleTimeString() : '--:--';
        const dir = signal.direction.toLowerCase();

        return `
            <div class="history-item ${dir}">
                <div class="history-item-header">
                    <span class="history-direction">${signal.direction}</span>
                    <span class="history-time">${time}</span>
                </div>
                <div class="history-asset">${signal.asset} • ${signal.expiry} • ${signal.confidence}%</div>
            </div>
        `;
    }).join('');
}

// Record win/loss
async function recordResult(result) {
    try {
        const response = await fetch('/api/signal/result', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ result })
        });

        const data = await response.json();
        if (data.success) {
            updateStats(data.stats);

            // Get signal ID from response or current signal
            const signalId = data.signal_id || (currentSignal && currentSignal.id);

            // Show optional note modal
            if (signalId && typeof showTradeNoteModal === 'function') {
                showTradeNoteModal(signalId);
            }

            // Hide quick actions after recording
            setTimeout(() => {
                document.getElementById('quick-actions').style.display = 'none';
            }, 500);
        }
    } catch (err) {
        console.error('Failed to record result:', err);
    }
}

// Notification sound
function playNotificationSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVbDn77BdGAo+ltrzxnMpBSl+zPLaizsIGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSF1xe/glEILEly47OynVhMKQ5zd8sFuJAUuhM/z1YU2Bxto');
        audio.play().catch(() => { });
    } catch (e) { }
}
// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRecentSignals();
    loadRecentHistory();
});

// Load recent signals to check for active ones
window.loadRecentSignals = async function () {
    try {
        const res = await fetch('/api/history?limit=1');
        const data = await res.json();

        if (data.signals && data.signals.length > 0) {
            const signal = data.signals[0];
            // If signal has no result, it's still active
            if (!signal.result) {
                displaySignal(signal);
            } else {
                // If the active signal we were showing now has a result, clear display
                if (currentSignal && currentSignal.id === signal.id) {
                    const display = document.getElementById('signal-display');
                    display.innerHTML = '<div class="waiting-state"><div class="signal-icon-placeholder">📊</div><h3>WAITING FOR SIGNAL</h3><p>Press \'aa\' to capture charts, then \'c\' to analyze</p></div>';
                    document.getElementById('quick-actions').style.display = 'none';
                    currentSignal = null;
                }
            }
        }
    } catch (err) {
        console.error('Failed to load recent signals:', err);
    }
}

// Load history
window.loadRecentHistory = async function () {
    try {
        const res = await fetch('/api/history?limit=10');
        const data = await res.json();

        if (data.signals) {
            updateHistory(data.signals);
        }
        if (data.stats) {
            updateStats(data.stats);
        }
    } catch (err) {
        console.error('Failed to load history:', err);
    }
}
