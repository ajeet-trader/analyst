// Risk Management Page
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadDailyStatus();
    loadSuggestions();
});

// Load current settings
async function loadSettings() {
    try {
        const res = await fetch('/api/risk/settings');
        const settings = await res.json();

        document.getElementById('account-balance').value = settings.account_balance;
        document.getElementById('risk-per-trade').value = settings.risk_per_trade_percent;
        document.getElementById('daily-loss-limit').value = settings.max_daily_loss_percent;
        document.getElementById('max-consecutive').value = settings.max_consecutive_losses;
        document.getElementById('daily-target').value = settings.daily_profit_target;

        // Calculate position size
        calculatePosition(settings.account_balance, settings.risk_per_trade_percent);

    } catch (err) {
        console.error('Failed to load settings:', err);
    }
}

// Save settings
document.getElementById('risk-settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const settings = {
        account_balance: parseFloat(document.getElementById('account-balance').value),
        risk_per_trade_percent: parseFloat(document.getElementById('risk-per-trade').value),
        max_daily_loss_percent: parseFloat(document.getElementById('daily-loss-limit').value),
        max_consecutive_losses: parseInt(document.getElementById('max-consecutive').value),
        daily_profit_target: parseFloat(document.getElementById('daily-target').value)
    };

    try {
        const res = await fetch('/api/risk/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (res.ok) {
            alert('✅ Settings saved successfully!');
            calculatePosition(settings.account_balance, settings.risk_per_trade_percent);
            loadDailyStatus();
            loadSuggestions();
        }
    } catch (err) {
        console.error('Failed to save settings:', err);
        alert('❌ Failed to save settings');
    }
});

// Calculate position size
function calculatePosition(balance, riskPercent) {
    const positionSize = balance * (riskPercent / 100);
    const accountRisk = riskPercent;

    document.getElementById('recommended-size').textContent = `$${positionSize.toFixed(2)}`;
    document.getElementById('max-loss').textContent = `$${positionSize.toFixed(2)}`;
    document.getElementById('account-risk').textContent = `${accountRisk.toFixed(2)}%`;
    document.getElementById('risk-reward').textContent = '1:0.8';
}

// Load today's status
async function loadDailyStatus() {
    try {
        const res = await fetch('/api/risk/daily-status');
        const status = await res.json();

        document.getElementById('trades-today').textContent = status.trades_today;

        const pnl = status.pnl_today;
        const pnlEl = document.getElementById('pnl-today');
        pnlEl.textContent = `$${pnl.toFixed(2)}`;
        pnlEl.style.color = pnl >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';

        document.getElementById('consecutive-losses').textContent = status.consecutive_losses;

        const canTradeEl = document.getElementById('can-trade');
        canTradeEl.textContent = status.can_trade ? '✓' : '✗';
        canTradeEl.style.color = status.can_trade ? 'var(--accent-green)' : 'var(--accent-red)';

        // Show warning if exists
        const warningEl = document.getElementById('risk-warning');
        if (status.warning) {
            warningEl.textContent = '⚠️ ' + status.warning;
            warningEl.style.display = 'block';
        } else {
            warningEl.style.display = 'none';
        }

    } catch (err) {
        console.error('Failed to load daily status:', err);
    }
}

// Load suggestions
async function loadSuggestions() {
    try {
        const res = await fetch('/api/risk/suggestions');
        const suggestions = await res.json();

        const list = document.getElementById('suggestions-list');

        if (suggestions && suggestions.length > 0) {
            list.innerHTML = suggestions.map(s => `<li>${s}</li>`).join('');
        } else {
            list.innerHTML = '<li>No suggestions at this time. Keep trading smart!</li>';
        }

    } catch (err) {
        console.error('Failed to load suggestions:', err);
    }
}

// Auto-refresh every 10 seconds
setInterval(() => {
    loadDailyStatus();
}, 10000);
