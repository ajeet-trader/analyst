// Session Check for Dashboard
document.addEventListener('DOMContentLoaded', () => {
    checkSessionStatus();
    // Check every 10 seconds
    setInterval(checkSessionStatus, 10000);
});

async function checkSessionStatus() {
    try {
        const res = await fetch('/api/sessions/active');
        const data = await res.json();

        const banner = document.getElementById('session-warning-banner');
        const dashboard = document.querySelector('.dashboard');

        const badge = document.getElementById('mode-badge');

        if (!data.active) {
            // No active session - show warning
            if (badge) badge.style.display = 'none';

            if (!banner && dashboard) {
                const newBanner = document.createElement('div');
                newBanner.id = 'session-warning-banner';
                newBanner.className = 'session-warning-banner';
                newBanner.innerHTML = `
                    <div class="warning-content">
                        <span class="warning-icon">⚠️</span>
                        <div class="warning-text">
                            <strong>No Active Session</strong>
                            <p>Start a trading session to analyze charts and record trades</p>
                        </div>
                        <a href="/sessions" class="btn-start-session">Start Session →</a>
                    </div>
                `;

                // Insert after header
                const header = dashboard.querySelector('.header');
                if (header && header.nextSibling) {
                    dashboard.insertBefore(newBanner, header.nextSibling);
                } else {
                    dashboard.appendChild(newBanner);
                }
            }
        } else {
            // Active session exists - remove warning if present
            if (banner) {
                banner.remove();
            }

            const statusText = document.getElementById('status-text');
            const statusBar = document.querySelector('.status-bar');
            if (statusText) statusText.innerText = 'Active Session';
            if (statusBar) statusBar.classList.add('active');

            // Update mode badge
            if (badge) {
                badge.style.display = 'inline-block';
                const mode = data.mode || 'demo';
                badge.innerHTML = (mode === 'live' ? '⚡ ' : '🔹 ') + mode.toUpperCase() + ' MODE';
                badge.className = 'mode-badge ' + mode.toLowerCase();
            }
        }
    } catch (err) {
        console.error('Failed to check session:', err);
    }
}
