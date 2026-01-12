# Discipline Lockout System - Implementation Plan

## Overview
Fullscreen lockout modal that forces traders to take a break when triggered. Prevents impulsive trading by requiring completion of calming/educational activities.

## Trigger Conditions

1. **Automatic Triggers** (from Risk Manager):
   - 3 consecutive losses
   - Daily loss limit hit (e.g., -5%)
   - Max trades per day reached

2. **Manual Trigger**:
   - "I'm Tilting" button on dashboard
   - Hotkey: `Ctrl+Shift+T`

## Lockout Activities (User Choice)

| Activity | Duration | Description |
|----------|----------|-------------|
| 🧘 **Meditation** | 2 min | Breathing animation + calming audio |
| 🧩 **Sudoku** | Until solved | 4x4 or 6x6 puzzle (difficulty based on time) |
| 📚 **Tutorial** | 2 min | Random trading concept lesson |
| 👁️ **Look Away** | 2 min | Eye rest with countdown timer |
| 📖 **Analyze Trades** | 2 min | Review last 5 trades with AI insights |

## Emergency Exit
- Type `91i` (hidden, no visual indicator)
- Shows confirmation: "Are you sure? This defeats the purpose."
- Logs exit to journal as "Discipline Override"

---

## Technical Implementation

### File Structure
```
dashboard/
├── static/
│   ├── js/
│   │   ├── lockout_manager.js       # Main lockout controller
│   │   ├── activities/
│   │   │   ├── meditation.js        # Breathing animation
│   │   │   ├── sudoku.js            # Puzzle generator
│   │   │   ├── tutorial.js          # Lesson display
│   │   │   └── trade_review.js      # AI-powered review
│   ├── css/
│   │   └── lockout.css              # Fullscreen modal styles
│   └── audio/
│       ├── meditation_bell.mp3
│       └── ambient_calm.mp3
├── templates/
│   └── lockout_modal.html           # Lockout UI
└── lockout/
    ├── config.yaml                  # Trigger rules
    └── tutorials.json               # Trading lessons bank
```

### Core Components

#### 1. Lockout Manager (`lockout_manager.js`)
```javascript
class LockoutManager {
    constructor() {
        this.isLocked = false;
        this.startTime = null;
        this.selectedActivity = null;
        this.emergencyCode = '91i';
        this.emergencyBuffer = '';
    }

    trigger(reason) {
        // Show fullscreen modal
        // Disable all dashboard interactions
        // Log trigger reason
    }

    selectActivity(activity) {
        // Load activity module
        // Start timer
    }

    checkEmergencyExit(key) {
        // Track keystrokes for '91i'
    }

    unlock() {
        // Log completion
        // Remove modal
        // Re-enable dashboard
    }
}
```

#### 2. Meditation Activity
- **Visual**: Pulsing circle (inhale 4s, hold 4s, exhale 4s)
- **Audio**: Optional calming sounds
- **Timer**: 2 minutes countdown
- **Completion**: Auto-unlock after timer

#### 3. Sudoku Puzzle
- **Generator**: Use simple backtracking algorithm
- **Difficulty**: 4x4 (easy), 6x6 (medium)
- **Validation**: Real-time checking
- **Completion**: Unlock when solved correctly

#### 4. Tutorial System
- **Content**: JSON bank of 50+ trading concepts
- **Format**: Title, explanation, example, quiz question
- **Selection**: Random or based on recent mistakes
- **Completion**: Read + answer quiz correctly

#### 5. Trade Review
- **Data**: Fetch last 5 trades from journal
- **AI Analysis**: Gemini analyzes patterns/mistakes
- **Display**: Side-by-side comparison with insights
- **Completion**: User must acknowledge insights

---

## UI/UX Design

### Lockout Modal
```html
<div id="lockout-overlay" class="lockout-fullscreen">
    <div class="lockout-header">
        <h1>⏸️ Trading Paused</h1>
        <p class="lockout-reason">Triggered: 3 Consecutive Losses</p>
    </div>

    <div class="lockout-message">
        <p>Take a break. Choose an activity to continue:</p>
    </div>

    <div class="activity-grid">
        <button class="activity-card" data-activity="meditation">
            <span class="activity-icon">🧘</span>
            <h3>Meditate</h3>
            <p>2 min breathing exercise</p>
        </button>
        <!-- More activities... -->
    </div>

    <div id="activity-container"></div>
    
    <div class="lockout-timer">
        Time remaining: <span id="timer">2:00</span>
    </div>
</div>
```

### CSS Styling
```css
.lockout-fullscreen {
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(10, 14, 39, 0.98);
    backdrop-filter: blur(20px);
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.activity-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    max-width: 1000px;
}

.activity-card {
    background: linear-gradient(135deg, #1a1f3a, #2d3a5f);
    border: 2px solid var(--accent-blue);
    padding: 30px;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s;
}

.activity-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
}
```

---

## Integration Points

### 1. Risk Manager Integration
```python
# risk/risk_manager.py
def check_lockout_triggers(self):
    if self.consecutive_losses >= 3:
        return {'trigger': True, 'reason': '3 Consecutive Losses'}
    
    if self.daily_loss_percent >= self.settings['daily_loss_limit']:
        return {'trigger': True, 'reason': 'Daily Loss Limit Hit'}
    
    return {'trigger': False}
```

### 2. Dashboard API Endpoint
```python
# dashboard/app.py
@app.route('/api/lockout/trigger', methods=['POST'])
def trigger_lockout():
    reason = request.json.get('reason')
    # Broadcast to frontend via WebSocket
    socketio.emit('lockout_triggered', {'reason': reason})
    return jsonify({'success': True})

@app.route('/api/lockout/complete', methods=['POST'])
def complete_lockout():
    activity = request.json.get('activity')
    duration = request.json.get('duration')
    # Log to journal
    journal.add_entry({
        'type': 'lockout_completion',
        'activity': activity,
        'duration': duration
    })
    return jsonify({'success': True})
```

### 3. WebSocket Events
```javascript
// Listen for lockout trigger
socket.on('lockout_triggered', (data) => {
    lockoutManager.trigger(data.reason);
});
```

---

## Configuration File

```yaml
# lockout/config.yaml
triggers:
  consecutive_losses: 3
  daily_loss_percent: 5
  max_trades_per_day: 20

activities:
  meditation:
    enabled: true
    duration: 120  # seconds
    audio: "ambient_calm.mp3"
  
  sudoku:
    enabled: true
    difficulty: "medium"  # easy, medium, hard
  
  tutorial:
    enabled: true
    duration: 120
    quiz_required: true
  
  look_away:
    enabled: true
    duration: 120
  
  trade_review:
    enabled: true
    trades_count: 5
    ai_analysis: true

emergency_exit:
  enabled: true
  code: "91i"
  confirmation_required: true
  log_to_journal: true
```

---

## Tutorials Bank (Sample)

```json
{
  "tutorials": [
    {
      "id": 1,
      "title": "Risk Management 101",
      "content": "Never risk more than 2% of your account on a single trade...",
      "quiz": {
        "question": "What's the recommended risk per trade?",
        "options": ["1%", "2%", "5%", "10%"],
        "correct": 1
      }
    },
    {
      "id": 2,
      "title": "Emotional Trading",
      "content": "Trading while emotional leads to poor decisions...",
      "quiz": {
        "question": "What should you do after 3 losses?",
        "options": ["Trade more to recover", "Take a break", "Increase position size", "Switch strategies"],
        "correct": 1
      }
    }
  ]
}
```

---

## Implementation Steps

### Phase 1: Core Lockout (2-3 hours)
1. Create `lockout_manager.js`
2. Build fullscreen modal HTML/CSS
3. Implement emergency exit (`91i` detection)
4. Add WebSocket integration
5. Test basic lock/unlock flow

### Phase 2: Activities (4-5 hours)
1. **Meditation**: Breathing animation + timer
2. **Sudoku**: Generator + validator
3. **Tutorial**: JSON loader + quiz system
4. **Look Away**: Simple countdown
5. **Trade Review**: API integration with Gemini

### Phase 3: Integration (2 hours)
1. Connect to Risk Manager triggers
2. Add manual trigger button
3. Journal logging
4. Settings page controls

### Phase 4: Polish (1-2 hours)
1. Animations and transitions
2. Audio integration
3. Mobile responsiveness
4. Testing all activities

---

## Testing Checklist

- [ ] Lockout triggers on 3 consecutive losses
- [ ] Manual trigger button works
- [ ] All 5 activities load correctly
- [ ] Emergency exit `91i` works
- [ ] Timer countdown accurate
- [ ] Meditation audio plays
- [ ] Sudoku validates correctly
- [ ] Tutorial quiz scoring works
- [ ] Trade review fetches data
- [ ] Completion unlocks dashboard
- [ ] Journal logs all events
- [ ] No way to bypass (except emergency)

---

## Future Enhancements

1. **Adaptive Duration**: Longer lockout for repeated triggers
2. **Gamification**: Earn badges for completing activities
3. **Custom Activities**: User-uploaded meditation audio
4. **Social Accountability**: Share lockout stats with trading buddy
5. **AI Coach**: Personalized advice during lockout
