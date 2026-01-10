// Settings Page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadActiveStrategy();
    loadDatabaseStats();
});

// Strategy data
const STRATEGIES = {
    conservative: {
        name: 'Conservative',
        description: 'High confidence, longer expiries, requires patterns',
        rules: {
            minConfidence: '80%',
            allowedExpiry: '2m, 5m, 15m',
            patternsRequired: 'Yes',
            confluenceRequired: 'Yes'
        }
    },
    scalping: {
        name: 'Scalping',
        description: 'Fast trades, 1-2m expiry only, high frequency',
        rules: {
            minConfidence: '70%',
            allowedExpiry: '1m, 2m',
            patternsRequired: 'No',
            confluenceRequired: 'No'
        }
    },
    aggressive: {
        name: 'Aggressive',
        description: 'Lower confidence threshold, more trades, higher risk',
        rules: {
            minConfidence: '65%',
            allowedExpiry: '1m, 2m, 5m',
            patternsRequired: 'No',
            confluenceRequired: 'No'
        }
    },
    swing: {
        name: 'Swing Trading',
        description: 'Longer timeframes, bigger moves, 15m+ expiry',
        rules: {
            minConfidence: '75%',
            allowedExpiry: '5m, 15m, 30m',
            patternsRequired: 'Yes',
            confluenceRequired: 'Yes'
        }
    },
    trend_following: {
        name: 'Trend Following',
        description: 'Only trade WITH the trend, requires confluence',
        rules: {
            minConfidence: '75%',
            allowedExpiry: '2m, 5m, 15m',
            patternsRequired: 'Yes',
            confluenceRequired: 'Yes (All TFs)'
        }
    }
};

async function loadActiveStrategy() {
    try {
        const res = await fetch('/api/strategy/active');
        const data = await res.json();

        const strategySelect = document.getElementById('strategy-select');
        strategySelect.value = data.active_strategy || 'conservative';

        displayStrategyDetails(strategySelect.value);

    } catch (err) {
        console.error('Failed to load strategy:', err);
    }
}

function displayStrategyDetails(strategyName) {
    const strategy = STRATEGIES[strategyName];
    if (!strategy) return;

    const detailsHtml = `
        <div class="strategy-info">
            <h3>${strategy.name}</h3>
            <p>${strategy.description}</p>
            <div class="strategy-rules">
                <div class="rule-item">
                    <strong>Min Confidence:</strong> ${strategy.rules.minConfidence}
                </div>
                <div class="rule-item">
                    <strong>Allowed Expiry:</strong> ${strategy.rules.allowedExpiry}
                </div>
                <div class="rule-item">
                    <strong>Patterns Required:</strong> ${strategy.rules.patternsRequired}
                </div>
                <div class="rule-item">
                    <strong>Confluence Required:</strong> ${strategy.rules.confluenceRequired}
                </div>
            </div>
        </div>
    `;

    document.getElementById('strategy-details').innerHTML = detailsHtml;
}

// Update display when selection changes
document.getElementById('strategy-select').addEventListener('change', (e) => {
    displayStrategyDetails(e.target.value);
});

async function saveStrategy() {
    const strategy = document.getElementById('strategy-select').value;

    try {
        const res = await fetch('/api/strategy/active', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ strategy })
        });

        if (res.ok) {
            alert('✅ Strategy saved! It will apply to new signals.');
        } else {
            alert('❌ Failed to save strategy');
        }
    } catch (err) {
        console.error('Failed to save strategy:', err);
        alert('❌ Error saving strategy');
    }
}

async function loadDatabaseStats() {
    try {
        const res = await fetch('/api/database/stats');
        const stats = await res.json();

        document.getElementById('stat-total').textContent = stats.total_signals;
        document.getElementById('stat-completed').textContent = stats.completed_trades;
        document.getElementById('stat-db-size').textContent = `${stats.database_size_mb} MB`;
        document.getElementById('stat-journal-size').textContent = `${stats.journal_size_mb} MB`;

    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function cleanupOldData() {
    if (!confirm('Delete all signals older than 90 days? This cannot be undone!')) {
        return;
    }

    try {
        const res = await fetch('/api/database/cleanup', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            alert(`✅ Deleted ${data.deleted} old signals`);
            loadDatabaseStats();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (err) {
        console.error('Cleanup failed:', err);
        alert('❌ Cleanup failed');
    }
}

async function resetDatabase() {
    const confirm1 = confirm('⚠️ WARNING: This will DELETE ALL your trading data!');
    if (!confirm1) return;

    const confirm2 = confirm('Are you ABSOLUTELY SURE? This cannot be undone!');
    if (!confirm2) return;

    try {
        const res = await fetch('/api/database/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: true })
        });

        const data = await res.json();

        if (data.success) {
            alert('✅ Database reset successfully');
            loadDatabaseStats();
            window.location.href = '/';
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (err) {
        console.error('Reset failed:', err);
        alert('❌ Reset failed');
    }
}
