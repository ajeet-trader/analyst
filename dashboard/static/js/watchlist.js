// Asset Watchlist JavaScript
// Handles multi-asset performance tracking and visualization

// Load assets on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAssets();
    loadSuggestion();
    loadHeatmap();

    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadAssets();
        loadSuggestion();
        loadHeatmap();
    }, 30000);
});

async function loadAssets() {
    try {
        const res = await fetch('/api/assets/list');
        const data = await res.json();

        if (data.success && data.assets && data.assets.length > 0) {
            renderAssetCards(data.assets);
        } else {
            document.getElementById('assets-grid').innerHTML = `
                <div class="empty-state">No assets tracked yet. Start capturing signals to build your watchlist!</div>
            `;
        }
    } catch (err) {
        console.error('Failed to load assets:', err);
    }
}

function renderAssetCards(assets) {
    const grid = document.getElementById('assets-grid');

    grid.innerHTML = assets.map(asset => {
        const winRate = asset.win_rate || 0;
        const payout = asset.avg_payout || 0;
        const totalProfit = asset.total_profit || 0;

        // Status indicator
        let statusClass = 'neutral';
        let statusIcon = '⚪';
        let statusText = 'Neutral';

        if (winRate >= 70 && asset.current_streak >= 2 && asset.streak_type === 'win') {
            statusClass = 'hot';
            statusIcon = '🔥';
            statusText = 'HOT';
        } else if (winRate <= 50 || (asset.streak_type === 'loss' && asset.current_streak >= 2)) {
            statusClass = 'cold';
            statusIcon = '🧊';
            statusText = 'COLD';
        }

        // Time since last check
        let timeSince = 'Never';
        if (asset.last_checked) {
            const lastCheck = new Date(asset.last_checked);
            const now = new Date();
            const diffMs = now - lastCheck;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);

            if (diffMins < 60) {
                timeSince = `${diffMins}m ago`;
            } else if (diffHours < 24) {
                timeSince = `${diffHours}h ago`;
            } else {
                const diffDays = Math.floor(diffHours / 24);
                timeSince = `${diffDays}d ago`;
            }
        }

        return `
            <div class="asset-card ${statusClass}" data-asset="${asset.asset_name}" onclick="showAssetDetails('${asset.asset_name}')" style="cursor: pointer;">
                <div class="asset-header">
                    <h3>${asset.asset_name}</h3>
                    <div class="asset-status ${statusClass}">
                        ${statusIcon} ${statusText}
                    </div>
                </div>
                
                <div class="asset-stats">
                    <div class="stat">
                        <div class="stat-label">Win Rate</div>
                        <div class="stat-value">${winRate.toFixed(1)}%</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Signals</div>
                        <div class="stat-value">${asset.total_signals}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Avg Payout</div>
                        <div class="stat-value">${payout.toFixed(1)}%</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Profit</div>
                        <div class="stat-value ${totalProfit >= 0 ? 'profit-positive' : 'profit-negative'}">
                            ${totalProfit >= 0 ? '+' : ''}$${totalProfit.toFixed(2)}
                        </div>
                    </div>
                </div>

                <div class="asset-insights">
                    ${Object.keys(asset.session_performance).length > 0 ? `
                        <div class="insight-item">
                            <span class="insight-label">Best Session:</span>
                            <span class="insight-value">${Object.entries(asset.session_performance)
                    .sort((a, b) => b[1].win_rate - a[1].win_rate)[0][0]}</span>
                        </div>
                    ` : ''}
                    ${asset.confidence_history.length > 1 ? `
                        <div class="insight-item">
                            <span class="insight-label">Confidence:</span>
                            <span class="insight-value">${asset.confidence_history.slice(-3).join(' → ')}%</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="asset-footer">
                    <div class="last-check">Last: ${timeSince}</div>
                    ${asset.current_streak > 0 ? `
                        <div class="streak">
                            ${asset.current_streak} ${asset.streak_type} streak
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function loadSuggestion() {
    try {
        const res = await fetch('/api/assets/suggest');
        const data = await res.json();

        if (data.success && data.suggestion) {
            const card = document.getElementById('suggestion-card');
            const assetEl = document.getElementById('suggested-asset');
            const reasonsEl = document.getElementById('suggestion-reasons');

            assetEl.textContent = data.suggestion.asset_name;
            reasonsEl.innerHTML = data.suggestion.reasons.map(r => `<div class="reason">• ${r}</div>`).join('');

            card.style.display = 'flex';
        }
    } catch (err) {
        console.error('Failed to load suggestion:', err);
    }
}

async function loadHeatmap() {
    try {
        const res = await fetch('/api/assets/heatmap');
        const data = await res.json();

        if (data.success && data.heatmap && Object.keys(data.heatmap).length > 0) {
            renderHeatmap(data.heatmap);
        }
    } catch (err) {
        console.error('Failed to load heatmap:', err);
    }
}

function renderHeatmap(heatmap) {
    const container = document.getElementById('heatmap');

    const assets = Object.entries(heatmap);

    container.innerHTML = `
        <table class="heatmap-table">
            <thead>
                <tr>
                    <th>Asset</th>
                    <th>Win Rate</th>
                    <th>Payout</th>
                    <th>Signals</th>
                    <th>Streak</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${assets.map(([name, data]) => {
        const winColor = data.win_rate >= 70 ? 'green' : data.win_rate >= 50 ? 'yellow' : 'red';
        const payoutColor = data.payout >= 90 ? 'green' : data.payout >= 85 ? 'yellow' : 'red';
        const statusColor = data.status === 'hot' ? 'green' : data.status === 'cold' ? 'red' : 'yellow';

        return `
                        <tr>
                            <td class="asset-name">${name}</td>
                            <td class="cell-${winColor}">${data.win_rate.toFixed(1)}%</td>
                            <td class="cell-${payoutColor}">${data.payout.toFixed(1)}%</td>
                            <td>${data.total_signals}</td>
                            <td>${data.streak}</td>
                            <td class="cell-${statusColor}">${data.status.toUpperCase()}</td>
                        </tr>
                    `;
    }).join('')}
            </tbody>
        </table>
    `;
}

// Asset Detail Modal
async function showAssetDetails(assetName) {
    try {
        const res = await fetch(`/api/assets/${encodeURIComponent(assetName)}/details`);
        const data = await res.json();

        if (!data.success) {
            alert('Failed to load asset details');
            return;
        }

        const details = data.details;
        renderAssetModal(details);
    } catch (err) {
        console.error('Failed to load asset details:', err);
        alert('Error loading asset details');
    }
}

function renderAssetModal(details) {
    // Check if modal already exists, if not create it
    let modal = document.getElementById('asset-detail-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'asset-detail-modal';
        modal.className = 'asset-modal';
        document.body.appendChild(modal);
    }

    const winRate = details.win_rate || 0;
    const avgPayout = details.avg_payout || 0;
    const totalProfit = details.total_profit || 0;

    // Session performance section
    let sessionPerf = '';
    if (details.session_performance && Object.keys(details.session_performance).length > 0) {
        sessionPerf = `
            <div class="session-performance">
                <h3>📅 Session Performance</h3>
                <div class="session-stats">
                    ${Object.entries(details.session_performance).map(([session, data]) => `
                        <div class="session-card">
                            <div class="session-name">${session}</div>
                            <div class="session-winrate">${data.win_rate.toFixed(1)}%</div>
                            <div class="session-trades">${data.wins}W / ${data.losses}L</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Confidence trend
    let confidenceTrend = '';
    if (details.confidence_history && details.confidence_history.length > 0) {
        const trend = details.confidence_history.slice(-5).join('% → ');
        confidenceTrend = `
            <div class="confidence-trend">
                <h3>📈 Confidence Trend (Last 5)</h3>
                <p style="font-size: 1.2rem; color: var(--accent-blue);">${trend}%</p>
            </div>
        `;
    }

    // Recent trades table
    let tradesTable = '';
    if (details.recent_trades && details.recent_trades.length > 0) {
        tradesTable = `
            <div class="recent-trades">
                <h3>📋 Recent Trades</h3>
                <table class="trades-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Direction</th>
                            <th>Conf</th>
                            <th>Payout</th>
                            <th>Result</th>
                            <th>P&L</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${details.recent_trades.map(trade => {
            const time = new Date(trade.timestamp).toLocaleTimeString();
            const resultClass = trade.result === 'win' ? 'win' : trade.result === 'loss' ? 'loss' : 'pending';
            const profit = trade.profit || 0;
            return `
                                <tr>
                                    <td>${time}</td>
                                    <td class="${trade.direction.toLowerCase()}">${trade.direction}</td>
                                    <td>${trade.confidence}%</td>
                                    <td>${(trade.payout_percent || 0).toFixed(1)}%</td>
                                    <td class="${resultClass}">${trade.result || 'Pending'}</td>
                                    <td class="${profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                                        ${profit >= 0 ? '+' : ''}$${profit.toFixed(2)}
                                    </td>
                                </tr>
                            `;
        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    modal.innerHTML = `
        <div class="modal-content glass-morphism">
            <div class="modal-header">
                <h2>${details.asset_name}</h2>
                <button class="modal-close" onclick="closeAssetModal()">×</button>
            </div>

            <div class="modal-body">
                <div class="asset-overview">
                    <div class="overview-stat">
                        <div class="stat-label">Win Rate</div>
                        <div class="stat-value">${winRate.toFixed(1)}%</div>
                    </div>
                    <div class="overview-stat">
                        <div class="stat-label">Avg Payout</div>
                        <div class="stat-value">${avgPayout.toFixed(1)}%</div>
                    </div>
                    <div class="overview-stat">
                        <div class="stat-label">Total Profit</div>
                        <div class="stat-value ${totalProfit >= 0 ? 'profit-positive' : 'profit-negative'}">
                            ${totalProfit >= 0 ? '+' : ''}$${totalProfit.toFixed(2)}
                        </div>
                    </div>
                    <div class="overview-stat">
                        <div class="stat-label">Signals</div>
                        <div class="stat-value">${details.total_signals}</div>
                    </div>
                </div>

                ${sessionPerf}
                ${confidenceTrend}
                ${tradesTable}
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

function closeAssetModal() {
    const modal = document.getElementById('asset-detail-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('asset-detail-modal');
    if (modal && e.target === modal) {
        closeAssetModal();
    }
});
