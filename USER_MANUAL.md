# User Manual - AI Trading Analyst

## Getting Started

### 1. First Run
```bash
python main.py
```
- Dashboard opens in browser at http://127.0.0.1:5000
- Console shows hotkey guide

### 2. Capture Charts
1. Open your trading platform (e.g., Quotex)
2. Navigate to chart you want to analyze
3. Press `aa` (double-a) to capture
4. Repeat for multiple timeframes (1m, 2m, 5m)
5. See "Captured #X" in console

### 3. Analyze
1. Press `c` to analyze captured charts
2. Wait 2-4 seconds for AI
3. Signal appears in dashboard + desktop notification

### 4. Record Results
- Click **WIN** or **LOSS** button after trade expires
- Stats update automatically

---

## Optimal Capture Timing

| Expiry | Capture Before Close |
|--------|---------------------|
| 1m | 10-15 seconds |
| 2m | 10-15 seconds |
| 5m | 20-30 seconds |

**Formula:** Capture = Candle close - 10 seconds

---

## Troubleshooting

### "No AI providers available"
- Check `.env` file has API keys
- At least one provider needs a valid key

### Signal quality issues
- Capture clear, uncluttered charts
- Include multiple timeframes
- Avoid capturing during high volatility news

### Dashboard not opening
- Check port 5000 is free
- Try: http://127.0.0.1:5000 manually

### No desktop notification
- Check Windows notification settings
- Enable notifications for Python

---

## Improving Results

### If accuracy drops:
1. **Check prompt file:** `ai/prompt_templates.py`
2. **Adjust patterns:** Add/remove pattern rules
3. **Tune confidence:** Change minimum threshold

### To add new patterns:
Edit `prompt_templates.py` → Pattern Recognition section

### To change expiry logic:
Edit `prompt_templates.py` → Expiry Calculation section

---

## Config Options

Edit `config.py`:

```python
# Enable/disable AI providers
ENABLE_GROQ = True
ENABLE_HUGGINGFACE = True
ENABLE_TOGETHER = True
ENABLE_GEMINI = False  # Disabled by default
ENABLE_OPENAI = False  # Disabled by default

# Sound alerts
ENABLE_SOUNDS = True
```

---

## Files to Modify for Customization

| Goal | File |
|------|------|
| Change AI logic | `ai/prompt_templates.py` |
| Add AI provider | `ai/[provider]_analyzer.py` |
| Modify UI | `dashboard/templates/index.html` |
| Change styling | `dashboard/static/css/style.css` |
| Update config | `config.py` |

---

## Evolving the Project

### Adding Features
1. Create new module in appropriate folder
2. Import in main.py or dashboard/app.py
3. Update config.py if needed
4. Test thoroughly

### Minimal Changes Principle
- Edit existing files over creating new ones
- Use config flags for on/off features
- Keep AI prompts modular

### Testing Changes
```bash
# Test single module
python -c "from ai.analyzer_factory import test_providers; test_providers()"

# Test full app
python main.py
```
