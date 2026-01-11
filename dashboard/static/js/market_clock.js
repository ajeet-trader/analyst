class MarketClock {
    constructor() {
        this.timeDisplay = document.getElementById('ist-clock');
        this.sessions = {
            'tokyo': { start: 0, end: 9, label: 'Tokyo' },
            'london': { start: 8, end: 16.5, label: 'London' },
            'new-york': { start: 13.5, end: 20, label: 'New York' },
            'sydney': { start: 22, end: 7, label: 'Sydney' } // Crosses midnight
        };

        this.peakHours = { start: 13.5, end: 16.5 }; // London + NY overlap

        if (this.timeDisplay) {
            this.update();
            setInterval(() => this.update(), 1000);
        }
    }

    update() {
        const now = new Date();

        // Update IST Clock
        // IST is UTC + 5:30
        const istTime = new Date(now.getTime() + (5.5 * 60 * 60 * 1000));
        // We only want to display the time relative to UTC for consistency in calculations,
        // but the display should be IST.
        // Actually, let's just use .toLocaleString with timeZone 'Asia/Kolkata'

        const istString = now.toLocaleTimeString('en-US', {
            timeZone: 'Asia/Kolkata',
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        if (this.timeDisplay) {
            this.timeDisplay.textContent = `IST ${istString}`;
        }

        // Check Sessions (using UTC hours)
        const utcHour = now.getUTCHours() + (now.getUTCMinutes() / 60);

        Object.keys(this.sessions).forEach(key => {
            const session = this.sessions[key];
            const statusEl = document.getElementById(`session-${key}`);
            if (!statusEl) return;

            const status = this.getSessionStatus(utcHour, session.start, session.end);
            this.updateSessionUI(statusEl, status);
        });

        // Check Peak Hours
        const peakEl = document.getElementById('market-peak');
        if (peakEl) {
            const isPeak = utcHour >= this.peakHours.start && utcHour < this.peakHours.end;
            if (isPeak) {
                peakEl.classList.add('active');
                peakEl.innerHTML = '🔥 PEAK VOLATILITY';
            } else {
                peakEl.classList.remove('active');
                peakEl.innerHTML = '⚡ NORMAL VOLATILITY';
            }
        }
    }

    getSessionStatus(current, start, end) {
        // Handle wrapping for Sydney (22 to 7)
        let isOpen = false;
        if (start < end) {
            isOpen = current >= start && current < end;
        } else {
            isOpen = current >= start || current < end;
        }

        if (isOpen) return 'OPEN';

        // Check Pre-market (30 mins before start)
        // Normalize time to handle midnight crossing logic for pre-market
        let preStart = start - 0.5;
        if (preStart < 0) preStart += 24;

        let isPre = false;
        // Pre-market is 30 mins interval [start-0.5, start)
        // If start crosses midnight (e.g. 00:00), pre-start is 23:30.
        // Simple distance check might be easier

        // Calculate distance to start
        let dist = start - current;
        if (dist < 0) dist += 24;

        if (dist <= 0.5 && dist > 0) return 'PRE';

        return 'CLOSED';
    }

    updateSessionUI(element, status) {
        const indicator = element.querySelector('.status-dot');
        const text = element.querySelector('.status-text');

        element.classList.remove('status-open', 'status-closed', 'status-pre');

        if (status === 'OPEN') {
            element.classList.add('status-open');
            if (text) text.textContent = 'OPEN';
        } else if (status === 'PRE') {
            element.classList.add('status-pre');
            if (text) text.textContent = 'PRE-MKT';
        } else {
            element.classList.add('status-closed');
            if (text) text.textContent = 'CLOSED';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MarketClock();
});
