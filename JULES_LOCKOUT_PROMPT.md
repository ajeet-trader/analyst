# JULES PROMPT: Discipline Lockout System Implementation

## Context
You are implementing a **Discipline Lockout System** for the Analyst AI trading dashboard. This is a fullscreen modal that forces traders to take a break when they're tilting or have hit risk limits.

## Project Location
- **Directory**: `j:\New folder`
- **Current Branch**: `dev3`
- **Implementation Plan**: `lockout_plan.md` (read this first!)

---

## Your Mission

Implement the Discipline Lockout System following the detailed plan in `lockout_plan.md`.

**Priority**: Complete Phase 1 & Phase 2 first (Core Lockout + Activities)

### What to Build

1. **Core Lockout System** (`lockout_manager.js`)
   - Fullscreen modal overlay (z-index: 99999)
   - Emergency exit detection (`91i` keystroke sequence)
   - WebSocket listener for trigger events
   - Activity selection menu
   - Timer countdown display

2. **Activities** (5 total):
   - 🧘 **Meditation**: Breathing circle animation (4s inhale, 4s hold, 4s exhale) + 2min timer
   - 🧩 **Sudoku**: 4x4 puzzle generator + real-time validation
   - 📚 **Tutorial**: Random lesson from `lockout/tutorials.json` + quiz
   - 👁️ **Look Away**: Simple 2min countdown
   - 📖 **Trade Review**: Fetch last 5 trades + display with AI summary

3. **Integration**:
   - Add trigger check to `risk/risk_manager.py`
   - Create API endpoints in `dashboard/app.py`:
     - `POST /api/lockout/trigger`
     - `POST /api/lockout/complete`
   - Add manual trigger button to dashboard header
   - Log all lockout events to journal

---

## File Structure to Create

```
dashboard/
├── static/
│   ├── js/
│   │   ├── lockout_manager.js       # ← START HERE
│   │   └── activities/
│   │       ├── meditation.js
│   │       ├── sudoku.js
│   │       ├── tutorial.js
│   │       ├── look_away.js
│   │       └── trade_review.js
│   ├── css/
│   │   └── lockout.css              # ← Fullscreen styles
│   └── audio/
│       └── meditation_bell.mp3      # ← Optional (can skip)
└── lockout/
    ├── config.yaml                  # ← Trigger rules
    └── tutorials.json               # ← 10+ trading lessons
```

---

## Implementation Steps

### Step 1: Core Lockout (START HERE)
1. Create `dashboard/static/js/lockout_manager.js`
2. Create `dashboard/static/css/lockout.css`
3. Add lockout modal HTML to `dashboard/templates/index.html`
4. Implement emergency exit (`91i` detection)
5. Test basic lock/unlock flow

**Test**: Manually trigger lockout from browser console: `lockoutManager.trigger('test')`

### Step 2: Meditation Activity
1. Create `dashboard/static/js/activities/meditation.js`
2. Build pulsing circle animation (CSS + JS)
3. Add 2-minute countdown timer
4. Auto-unlock when complete

**Test**: Select meditation, verify 2min countdown, verify auto-unlock

### Step 3: Sudoku Activity
1. Create `dashboard/static/js/activities/sudoku.js`
2. Implement 4x4 sudoku generator (simple backtracking)
3. Add input validation (highlight errors in red)
4. Unlock when puzzle solved correctly

**Test**: Generate puzzle, solve it, verify unlock

### Step 4: Tutorial System
1. Create `lockout/tutorials.json` with 10+ lessons
2. Create `dashboard/static/js/activities/tutorial.js`
3. Load random tutorial + display
4. Add quiz question (multiple choice)
5. Unlock after correct answer

**Test**: View tutorial, answer quiz, verify unlock

### Step 5: Integration with Risk Manager
1. Update `risk/risk_manager.py`:
   ```python
   def check_lockout_triggers(self):
       if self.consecutive_losses >= 3:
           return {'trigger': True, 'reason': '3 Consecutive Losses'}
       return {'trigger': False}
   ```

2. Add to `dashboard/app.py`:
   ```python
   @app.route('/api/lockout/trigger', methods=['POST'])
   def trigger_lockout():
       reason = request.json.get('reason')
       socketio.emit('lockout_triggered', {'reason': reason})
       return jsonify({'success': True})
   ```

3. Call from WIN/LOSS button logic:
   ```python
   lockout_check = risk_manager.check_lockout_triggers()
   if lockout_check['trigger']:
       socketio.emit('lockout_triggered', lockout_check)
   ```

### Step 6: Manual Trigger Button
1. Add button to dashboard header (next to mode badge):
   ```html
   <button class="btn-lockout" onclick="manualLockout()">
       🧘 Take Break
   </button>
   ```

2. Wire up to lockout manager

---

## Design Guidelines

### Visual Style
- **Background**: Dark overlay `rgba(10, 14, 39, 0.98)` with blur
- **Cards**: Glass morphism effect (same as other cards)
- **Colors**: Use existing CSS variables (`--accent-blue`, etc.)
- **Animations**: Smooth transitions (0.3s ease)

### UX Requirements
- **No way to close** except completing activity or `91i`
- **Clear instructions** for each activity
- **Timer always visible**
- **Progress indicators** (e.g., Sudoku cells filled)
- **Responsive** on all screen sizes

---

## Testing Checklist

After implementation, verify:

- [ ] Lockout triggers on 3 consecutive losses
- [ ] Manual trigger button works
- [ ] `91i` emergency exit prompts confirmation
- [ ] Meditation: Circle pulses correctly, timer counts down
- [ ] Sudoku: Puzzle generates, validation works, unlock on solve
- [ ] Tutorial: Random lesson loads, quiz scoring works
- [ ] Look Away: Timer works, auto-unlock
- [ ] Trade Review: Fetches trades, displays correctly
- [ ] No way to bypass (disable F11, Esc, etc.)
- [ ] Journal logs lockout completion
- [ ] Works on mobile (responsive)

---

## Code Snippets to Copy

### Emergency Exit Detection
```javascript
let emergencyBuffer = '';
document.addEventListener('keydown', (e) => {
    emergencyBuffer += e.key;
    if (emergencyBuffer.endsWith('91i')) {
        if (confirm('Exit lockout? This defeats the purpose.')) {
            this.unlock('emergency_exit');
        }
        emergencyBuffer = '';
    }
    if (emergencyBuffer.length > 10) emergencyBuffer = '';
});
```

### Breathing Animation (CSS)
```css
@keyframes breathe {
    0%, 100% { transform: scale(1); }
    33% { transform: scale(1.5); }  /* Inhale */
    66% { transform: scale(1.5); }  /* Hold */
}

.breathing-circle {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    animation: breathe 12s infinite;
}
```

### Simple Sudoku Generator (4x4)
```javascript
function generateSudoku4x4() {
    // Solved puzzle
    let solved = [
        [1, 2, 3, 4],
        [3, 4, 1, 2],
        [2, 3, 4, 1],
        [4, 1, 2, 3]
    ];
    
    // Remove 6 random cells
    let puzzle = JSON.parse(JSON.stringify(solved));
    for (let i = 0; i < 6; i++) {
        let r = Math.floor(Math.random() * 4);
        let c = Math.floor(Math.random() * 4);
        puzzle[r][c] = 0;
    }
    
    return { puzzle, solution: solved };
}
```

---

## Sample Tutorial Entry

```json
{
  "id": 1,
  "title": "The 3-Loss Rule",
  "content": "After 3 consecutive losses, your judgment is likely impaired by emotion. Taking a break allows you to reset mentally and return with a clear head. Professional traders follow strict rules to prevent revenge trading.",
  "quiz": {
    "question": "What should you do after 3 losses in a row?",
    "options": [
      "Trade more aggressively to recover",
      "Take a mandatory break",
      "Switch to a different asset",
      "Increase position size"
    ],
    "correct": 1
  }
}
```

---

## Error Handling

- Gracefully handle missing tutorials.json
- Fallback activities if one fails to load
- Never block user permanently (always allow `91i`)
- Log all errors to console

---

## Estimated Time
- **Phase 1 (Core)**: 1-2 hours
- **Phase 2 (Activities)**: 2-3 hours
- **Phase 3 (Integration)**: 1 hour
- **Testing**: 30 minutes

**Total**: ~5 hours

---

## Success Criteria

You're done when:
1. ✅ All 5 activities work
2. ✅ Auto-triggers work (3 losses)
3. ✅ Manual trigger works
4. ✅ Emergency exit works
5. ✅ No way to bypass
6. ✅ All tests pass
7. ✅ Code is clean and documented

---

## Questions? Check:
1. `lockout_plan.md` - Full technical spec
2. Existing code in `dashboard/static/js/` for patterns
3. `dashboard/static/css/style.css` for CSS variables

## Git Workflow
- Work on branch `dev3`
- Commit frequently with clear messages
- Push when Phase 1 + Phase 2 complete

---

Good luck Jules! This is a high-impact feature that will genuinely help traders. 🚀
