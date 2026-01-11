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
        // Navigate to dedicated session detail page
        window.location.href = `/sessions/${sessionId}`;
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
        const res = await fetch(`/api/sessions/${sessionId}/resume`, {
            method: 'POST'
        });
        const data = await res.json();

        if (data.success) {
            alert('✅ Session resumed!');
            loadSessions();
        }
    } catch (err) {
        console.error('Failed to resume session:', err);
    }
}
