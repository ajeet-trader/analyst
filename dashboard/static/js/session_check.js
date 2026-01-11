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

            // Update mode badge
            if (badge) {
                badge.style.display = 'inline-block';
                const mode = data.mode || 'demo';
                if (mode === 'live') {
                    badge.innerHTML = '🟢 LIVE MODE';
                    badge.style.background = 'rgba(16, 185, 129, 0.2)';
                    badge.style.color = '#10b981';
                    badge.style.border = '1px solid #10b981';
                } else {
                    badge.innerHTML = '🔵 DEMO MODE';
                    badge.style.background = 'rgba(59, 130, 246, 0.2)';
                    badge.style.color = '#3b82f6';
                    badge.style.border = '1px solid #3b82f6';
                }
            }
        }
    } catch (err) {
        console.error('Failed to check session:', err);
    }
}
