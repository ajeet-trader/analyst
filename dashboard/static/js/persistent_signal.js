// Persistent Signal Panel - Shows active signal on ALL pages
let currentActiveSignal = null;
let signalPollingInterval = null;
let persistentTimerInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    createPersistentSignalPanel();
    startSignalPolling();
});

function createPersistentSignalPanel() {
    // Check if panel already exists
    if (document.getElementById('persistent-signal-panel')) return;

    const panel = document.createElement('div');
    panel.id = 'persistent-signal-panel';
    panel.className = 'persistent-signal-panel';
    // No inline display: none - handled by .visible class in CSS
    panel.innerHTML = `
        <div class="persistent-signal-content glass-morphism">
            <div class="signal-badge-container">
                <div class="signal-direction-badge" id="persist-direction">--</div>
            </div>
            <div class="signal-details">
                <div class="signal-primary-info">
                    <span class="signal-asset-name" id="persist-asset">--</span>
                    <span class="signal-confidence-bar" id="persist-confidence">--</span>
                </div>
                <div class="signal-secondary-info">
                    <span class="signal-expiry-text">Expiry: <span id="persist-expiry">--</span></span>
                </div>
            </div>
            <div class="signal-timer-container">
                <span class="timer-label">Ends in:</span>
                <div class="signal-timer-clock" id="persist-timer">00:00</div>
            </div>
            <div class="signal-actions-modern">
                <button onclick="recordPersistentResult('win')" class="btn-modern-win">
                    <span class="icon">✓</span> WIN
                </button>
                <button onclick="recordPersistentResult('loss')" class="btn-modern-loss">
                    <span class="icon">✗</span> LOSS
                </button>
            </div>
        </div>
    `;

    // Insert after header - find header and insert after it
    const header = document.querySelector('header.header') || document.querySelector('.header');
    if (header) {
        if (header.nextSibling) {
            header.parentNode.insertBefore(panel, header.nextSibling);
        } else {
            header.parentNode.appendChild(panel);
        }
    } else {
        // Fallback: prepend to body
        document.body.prepend(panel);
    }

    console.log('Persistent signal panel created');
}

function startSignalPolling() {
    if (signalPollingInterval) clearInterval(signalPollingInterval);
    signalPollingInterval = setInterval(checkForActiveSignal, 2000);
    checkForActiveSignal(); // Initial check
}

async function checkForActiveSignal() {
    try {
        const res = await fetch(`/api/history?limit=1&t=${Date.now()}`);
        if (!res.ok) return;

        const data = await res.json();

        if (data.signals && data.signals.length > 0) {
            const signal = data.signals[0];

            // Only show if signal has no result yet
            if (!signal.result) {
                // If it's a new active signal, update
                if (!currentActiveSignal || currentActiveSignal.id !== signal.id) {
                    console.log('New active signal found:', signal);
                    currentActiveSignal = signal;
                    updatePersistentPanel(signal);
                }
                showPersistentPanel();
            } else {
                hidePersistentPanel();
            }
        } else {
            hidePersistentPanel();
        }
    } catch (err) {
        console.error('Failed to check for active signal:', err);
    }
}

function updatePersistentPanel(signal) {
    const dirEl = document.getElementById('persist-direction');
    const assetEl = document.getElementById('persist-asset');
    const confEl = document.getElementById('persist-confidence');
    const expEl = document.getElementById('persist-expiry');

    if (dirEl) {
        dirEl.textContent = signal.direction;
        dirEl.className = `signal-direction-badge ${signal.direction.toLowerCase()}`;
    }
    if (assetEl) assetEl.textContent = signal.asset;
    if (confEl) confEl.textContent = `${signal.confidence}%`;
    if (expEl) expEl.textContent = signal.expiry;

    // Start countdown timer
    startPersistentTimer(signal.timestamp, signal.expiry);
}

function parseExpiry(expiry) {
    if (!expiry) return 1;
    if (expiry.toLowerCase().endsWith('m')) {
        return parseInt(expiry) || 1;
    } else if (expiry.toLowerCase().endsWith('s')) {
        return parseInt(expiry) / 60;
    } else if (expiry.toLowerCase().endsWith('h')) {
        return parseInt(expiry) * 60;
    }
    return parseInt(expiry) || 1;
}

function startPersistentTimer(timestamp, expiry) {
    if (persistentTimerInterval) clearInterval(persistentTimerInterval);

    // Robust parsing for Local ISO timestamp
    const parseISO = (str) => {
        if (!str) return new Date();
        // Replace space with T if needed, or handle various formats
        const t = str.includes('T') ? str : str.replace(' ', 'T');
        return new Date(t);
    };

    const expiryMinutes = parseExpiry(expiry);
    const signalTime = parseISO(timestamp);
    const expiryTime = new Date(signalTime.getTime() + expiryMinutes * 60000);

    const updateTimer = () => {
        const now = new Date();
        const remaining = expiryTime - now;
        const timerEl = document.getElementById('persist-timer');

        if (!timerEl) return;

        if (remaining <= 0) {
            timerEl.textContent = 'EXPIRED';
            timerEl.classList.add('expired');
            return;
        }

        const minutes = Math.floor(remaining / 60000);
        const seconds = Math.floor((remaining % 60000) / 1000);
        timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        timerEl.classList.remove('expired');
    };

    updateTimer();
    persistentTimerInterval = setInterval(updateTimer, 1000);
}

function showPersistentPanel() {
    const panel = document.getElementById('persistent-signal-panel');
    if (panel) panel.classList.add('visible');
}

function hidePersistentPanel() {
    const panel = document.getElementById('persistent-signal-panel');
    if (panel) panel.classList.remove('visible');
    currentActiveSignal = null;
    if (persistentTimerInterval) {
        clearInterval(persistentTimerInterval);
        persistentTimerInterval = null;
    }
}

async function recordPersistentResult(result) {
    if (!currentActiveSignal) return;

    try {
        const res = await fetch(`/api/signals/${currentActiveSignal.id}/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ result })
        });

        if (res.ok) {
            hidePersistentPanel();
            // Optional: Show success toast instead of alert
            console.log(`Trade marked as ${result.toUpperCase()}`);

            // Trigger refresh on dashboard if present
            if (window.loadRecentSignals) {
                window.loadRecentSignals();
            }
        } else {
            const error = await res.json();
            console.error('Failed to record result:', error);
        }
    } catch (err) {
        console.error('Failed to record result:', err);
    }
}
