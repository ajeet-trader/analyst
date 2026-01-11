// Session Detail Page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadSessionDetails();
});

async function loadSessionDetails() {
    // Get session ID from URL
    const pathParts = window.location.pathname.split('/');
    const sessionId = pathParts[pathParts.length - 1];

    if (!sessionId || sessionId === 'sessions') {
        window.location.href = '/sessions';
        return;
    }

    try {
        const res = await fetch(`/api/sessions/${sessionId}/details`);
        const data = await res.json();

        if (!data.success) {
            alert('Session not found');
            window.location.href = '/sessions';
            return;
        }

        renderSessionDetails(data.session);
    } catch (err) {
        console.error('Failed to load session:', err);
        alert('Error loading session details');
    }
}

function renderSessionDetails(session) {
    // Session header
    document.getElementById('session-name').textContent = session.name || `Session ${session.id}`;

    const statusBadge = document.getElementById('session-status');
    statusBadge.textContent = session.status.toUpperCase();
    statusBadge.className = `status-badge status-${session.status.toLowerCase()}`;

    // Session metadata
    const startDate = new Date(session.started_at);
    document.getElementById('session-date').textContent = startDate.toLocaleString();
    document.getElementById('session-duration').textContent = session.duration || 'Ongoing';

    // Calculate stats
    const trades = session.trades || [];
    const wins = trades.filter(t => t.result === 'win').length;
    const losses = trades.filter(t => t.result === 'loss').length;
    const totalTrades = trades.length;
    const winRate = totalTrades > 0 ? ((wins / totalTrades) * 100).toFixed(1) : 0;

    // Calculate average payout
    const payouts = trades.map(t => t.payout_percent || 0).filter(p => p > 0);
    const avgPayout = payouts.length > 0
        ? (payouts.reduce((a, b) => a + b, 0) / payouts.length).toFixed(1)
        : 0;

    // Calculate total P&L
    const totalPL = trades.reduce((sum, t) => sum + (t.profit || 0), 0);

    // Update stats
    document.getElementById('total-trades').textContent = totalTrades;
    document.getElementById('wins').textContent = wins;
    document.getElementById('losses').textContent = losses;
    document.getElementById('win-rate').textContent = `${winRate}%`;
    document.getElementById('avg-payout').textContent = `${avgPayout}%`;

    const plElement = document.getElementById('total-pl');
    plElement.textContent = `${totalPL >= 0 ? '+' : ''}$${totalPL.toFixed(2)}`;
    plElement.className = `stat-value ${totalPL >= 0 ? 'stat-profit' : 'stat-loss'}`;

    // Render trades table
    renderTradesTable(trades);
}

function renderTradesTable(trades) {
    const tbody = document.getElementById('trades-tbody');

    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No trades in this session</td></tr>';
        return;
    }

    tbody.innerHTML = trades.map(trade => {
        const time = new Date(trade.timestamp).toLocaleTimeString();
        const directionClass = trade.direction.toLowerCase();
        const resultClass = trade.result === 'win' ? 'win' : trade.result === 'loss' ? 'loss' : 'pending';
        const profit = trade.profit || 0;
        const hasCharts = trade.charts && trade.charts.length > 0;

        return `
            <tr>
                <td>${time}</td>
                <td>${trade.asset}</td>
                <td class="direction-${directionClass}">
                    <span class="direction-badge ${directionClass}">${trade.direction}</span>
                </td>
                <td>${trade.confidence}%</td>
                <td style="color: var(--accent-blue); font-weight: 600;">${(trade.payout_percent || 0).toFixed(1)}%</td>
                <td>${trade.expiry}</td>
                <td>
                    <span class="result-badge ${resultClass}">
                        ${trade.result ? trade.result.toUpperCase() : 'PENDING'}
                    </span>
                </td>
                <td class="${profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                    ${profit >= 0 ? '+' : ''}$${profit.toFixed(2)}
                </td>
                <td>
                    ${hasCharts
                ? `<button class="btn-view-charts" onclick="viewCharts(${trade.id}, ${JSON.stringify(trade.charts).replace(/"/g, '&quot;')})">📸 View</button>`
                : '<span style="color: var(--text-secondary);">None</span>'
            }
                </td>
            </tr>
        `;
    }).join('');
}

function viewCharts(tradeId, charts) {
    const modal = document.getElementById('chart-modal');
    const carousel = document.getElementById('chart-carousel');

    carousel.innerHTML = charts.map((chartPath, index) => {
        // Extract filename from path
        const filename = chartPath.split('/').pop();
        return `
            <div class="chart-slide">
                <img src="/archive/${filename}" alt="Chart ${index + 1}" />
            </div>
        `;
    }).join('');

    modal.style.display = 'flex';
}

function closeChartModal() {
    document.getElementById('chart-modal').style.display = 'none';
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('chart-modal');
    if (e.target === modal) {
        closeChartModal();
    }
});
