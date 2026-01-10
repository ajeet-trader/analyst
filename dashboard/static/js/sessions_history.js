// Sessions History Page
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
});

async function loadSessions() {
    try {
        const res = await fetch('/api/sessions/all');
        const sessions = await res.json();

        const tbody = document.getElementById('sessions-tbody');

        if (sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="empty">No sessions yet. Start your first session!</td></tr>';
            return;
        }

        tbody.innerHTML = sessions.map(session => {
            const stats = session.stats || {};
            const duration = calculateSessionDuration(session.start_time, session.end_time);
            const statusBadge = getStatusBadge(session.status);
            const winRate = stats.win_rate || 0;
            const pnl = stats.total_pnl || 0;

            return `
                <tr>
                    <td class="session-name-cell">${session.session_name}</td>
                    <td>${formatDate(session.start_time)}</td>
                    <td>${duration}</td>
                    <td>${session.strategy_name || 'N/A'}</td>
                    <td>${stats.total_signals || 0}</td>
                    <td>${winRate.toFixed(1)}%</td>
                    <td class="${pnl >= 0 ? 'profit' : 'loss'}">$${pnl.toFixed(2)}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button onclick="viewSessionDetails(${session.id})" class="btn-view">👁 View</button>
                        ${session.status === 'paused' ? `<button onclick="resumeSession(${session.id})" class="btn-resume">▶ Resume</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error('Failed to load sessions:', err);
        document.getElementById('sessions-tbody').innerHTML =
            '<tr><td colspan="9" class="error">Failed to load sessions</td></tr>';
    }
}

function calculateSessionDuration(start, end) {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    const diff = Math.floor((endTime - startTime) / 1000); // seconds

    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getStatusBadge(status) {
    const badges = {
        'active': '<span class="badge badge-active">Active</span>',
        'paused': '<span class="badge badge-paused">Paused</span>',
        'completed': '<span class="badge badge-completed">Completed</span>'
    };
    return badges[status] || status;
}

async function viewSessionDetails(sessionId) {
    try {
        const res = await fetch(`/api/sessions/${sessionId}/details`);
        const session = await res.json();

        if (!session || !session.id) {
            alert('Session not found');
            return;
        }

        const stats = session.stats || {};
        const signals = session.signals || [];

        const modalBody = document.getElementById('session-modal-body');
        modalBody.innerHTML = `
            <h2>${session.session_name}</h2>
            
            <div class="session-details-grid">
                <div class="detail-card">
                    <h3>Overview</h3>
                    <p><strong>Started:</strong> ${formatDate(session.start_time)}</p>
                    <p><strong>Ended:</strong> ${session.end_time ? formatDate(session.end_time) : 'Ongoing'}</p>
                    <p><strong>Duration:</strong> ${calculateSessionDuration(session.start_time, session.end_time)}</p>
                    <p><strong>Strategy:</strong> ${session.strategy_name}</p>
                    <p><strong>Status:</strong> ${getStatusBadge(session.status)}</p>
                </div>
                
                <div class="detail-card">
                    <h3>Performance</h3>
                    <p><strong>Total Trades:</strong> ${stats.total_signals}</p>
                    <p><strong>Wins:</strong> ${stats.wins}</p>
                    <p><strong>Losses:</strong> ${stats.losses}</p>
                    <p><strong>Win Rate:</strong> ${stats.win_rate.toFixed(1)}%</p>
                    <p><strong>P&L:</strong> <span class="${stats.total_pnl >= 0 ? 'profit' : 'loss'}">$${stats.total_pnl.toFixed(2)}</span></p>
                </div>
            </div>
            
            ${session.notes ? `<div class="session-notes"><h3>Notes</h3><p>${session.notes}</p></div>` : ''}
            
            <h3>Trades in Session</h3>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Asset</th>
                        <th>Direction</th>
                        <th>Confidence</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
                    ${signals.map(sig => `
                        <tr>
                            <td>${formatDate(sig.timestamp)}</td>
                            <td>${sig.asset}</td>
                            <td class="${sig.direction.toLowerCase()}">${sig.direction}</td>
                            <td>${sig.confidence}%</td>
                            <td>${sig.result ? `<span class="badge badge-${sig.result}">${sig.result}</span>` : 'Pending'}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="5">No trades yet</td></tr>'}
                </tbody>
            </table>
        `;

        document.getElementById('session-modal').style.display = 'flex';

    } catch (err) {
        console.error('Failed to load session details:', err);
        alert('Failed to load session details');
    }
}

function closeSessionModal() {
    document.getElementById('session-modal').style.display = 'none';
}

async function resumeSession(sessionId) {
    try {
        const res = await fetch(`/api/sessions/${sessionId}/resume`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            alert('✅ Session resumed!');
            loadSessions();
        }
    } catch (err) {
        console.error('Failed to resume session:', err);
    }
}
