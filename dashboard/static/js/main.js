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
    startCountdown(signal.expiry);
}

function displayError(error) {
    const display = document.getElementById('signal-display');
    display.innerHTML = `
        <div class="signal-active" style="border-left: 3px solid var(--accent-red)">
            <div class="signal-direction">
                <span class="signal-arrow" style="color: var(--accent-red)">⚠</span>
                <span class="signal-text" style="color: var(--accent-red)">ERROR</span>
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

function startCountdown(expiry) {
    if (timerInterval) clearInterval(timerInterval);

    // Parse expiry to seconds
    let seconds = 60; // default 1m
    const exp = expiry.toLowerCase();
    if (exp.includes('s')) {
        seconds = parseInt(exp);
    } else if (exp.includes('m')) {
        seconds = parseInt(exp) * 60;
    }

    const countdown = document.getElementById('countdown');

    timerInterval = setInterval(() => {
        if (seconds <= 0) {
            clearInterval(timerInterval);
            countdown.textContent = 'EXPIRED';
            countdown.classList.add('warning');
            return;
        }

        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        countdown.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        if (seconds <= 10) {
            countdown.classList.add('warning');
        }

        seconds--;
    }, 1000);
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
        const time = signal.timestamp ? new Date(signal.timestamp).toLocaleTimeString() : '--:--';
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
