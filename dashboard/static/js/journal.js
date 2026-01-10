// Journal Page - Display archived trades
document.addEventListener('DOMContentLoaded', () => {
    loadJournal();
});

async function loadJournal() {
    try {
        const res = await fetch('/api/journal/recent?limit=50');
        const trades = await res.json();

        displayJournal(trades);
    } catch (err) {
        console.error('Failed to load journal:', err);
    }
}

function displayJournal(trades) {
    const container = document.getElementById('journal-list');

    if (!trades || trades.length === 0) {
        container.innerHTML = '<p class="empty-state">No trades journaled yet</p>';
        return;
    }

    container.innerHTML = trades.map(trade => {
        const timestamp = new Date(trade.timestamp).toLocaleString();
        const result = trade.result || 'pending';
        const resultClass = result === 'win' ? 'win' : result === 'loss' ? 'loss' : 'pending';
        const resultIcon = result === 'win' ? '✅' : result === 'loss' ? '❌' : '⏳';

        const suggestions = trade.post_analysis?.suggestions || [];

        return `
            <div class="journal-entry ${resultClass}">
                <div class="journal-header">
                    <div class="journal-title">
                        <span class="journal-result-icon">${resultIcon}</span>
                        <span class="journal-direction ${trade.direction.toLowerCase()}">${trade.direction}</span>
                        <span class="journal-asset">${trade.asset}</span>
                    </div>
                    <div class="journal-meta">
                        <span class="journal-time">${timestamp}</span>
                        <span class="journal-confidence">${trade.confidence}%</span>
                    </div>
                </div>
                
                <div class="journal-details">
                    <div class="journal-info">
                        <strong>Expiry:</strong> ${trade.expiry} | 
                        <strong>Timing:</strong> ${trade.entry_timing} |
                        <strong>Provider:</strong> ${trade.provider}
                    </div>
                    
                    ${trade.patterns_detected && trade.patterns_detected.length > 0 ? `
                        <div class="journal-patterns">
                            <strong>Patterns:</strong> 
                            ${trade.patterns_detected.map(p => `<span class="pattern-badge">${p.replace(/_/g, ' ')}</span>`).join(' ')}
                        </div>
                    ` : ''}
                    
                    <div class="journal-reasoning">
                        <strong>💡 Reasoning:</strong> ${trade.reasoning || 'No reasoning provided'}
                    </div>
                    
                    ${trade.user_note ? `
                        <div class="journal-note">
                            <strong>📝 Note:</strong> ${trade.user_note}
                        </div>
                    ` : ''}
                    
                    ${suggestions.length > 0 ? `
                        <div class="journal-suggestions">
                            <strong>💭 Suggestions:</strong>
                            <ul>
                                ${suggestions.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="journal-charts">
                        ${trade.charts && trade.charts.length > 0 ?
                trade.charts.map((chart, i) =>
                    `<div class="journal-chart-thumb">
                                    <img src="/archive/${chart.split('archives/')[1] || chart}" alt="Chart ${i + 1}" />
                                </div>`
                ).join('')
                : '<p class="empty-state">No charts archived</p>'
            }
                    </div>
                </div>
            </div>
        `;
    }).join('');
}
