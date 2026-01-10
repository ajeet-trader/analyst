# AI Trading Analyst - User Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup API Keys**
   - Copy `.env.example` to `.env`
   - Add at least ONE API key:
     - Groq (FREE): https://console.groq.com
     - HuggingFace (FREE): https://huggingface.co/settings/tokens
     - Together AI (FREE): https://api.together.xyz

3. **Run the App**
   ```bash
   python main.py
   ```

4. **Open Dashboard**
   - Automatically opens at http://127.0.0.1:5000
   - Or manually visit the URL

---

## How to Use

### Capturing Charts

1. Open your trading platform
2. Press `aa` to capture 3 screenshots
3. Charts are saved to cache

### Analyzing Signals

1. After capturing, press `c` to analyze
2. AI processes your charts (2-4 seconds)
3. Signal appears on dashboard + desktop notification

### Recording Results

1. After trade expires, click:
   - **✓ WIN** - Mark as winning trade
   - **✗ LOSS** - Mark as losing trade
2. Results automatically save to database and journal

---

## Dashboard Pages

### 1. Main Dashboard (/)
- Live signal display
- Chart thumbnails
- Win/loss stats
- Signal history

### 2. Analytics (/analytics)
- Performance by asset
- Performance by pattern
- 30-day timeline chart
- Overall statistics

### 3. Journal (/journal)
- Archived trades with charts
- Post-trade analysis
- Improvement suggestions
- Complete trade history

---

## Hotkeys

| Key | Action |
|-----|--------|
| `aa` | Capture 3 screenshots |
| `c` | Analyze captured charts |
| `x` | Clear cache |
| `v` | View cache folder |
| `q` | Quit application |

---

## Best Practices

### Timing
- Capture 10-15 seconds before candle close
- Use multiple timeframes (1m, 2m, 5m)
- Wait for AI analysis (2-4 seconds)

### Risk Management
- Start with demo account
- Never risk more than you can afford to lose
- Don't blindly follow signals
- Use signals as ONE tool, not the only tool

### Signal Interpretation
- **80%+ confidence** - Strong signal
- **70-79% confidence** - Moderate signal
- **Below 70%** - Weak signal, consider skipping

---

## Configuration

Edit `dashboard/config.py` to customize:
- History limits
- Chart refresh rates
- Notification settings
- Feature flags
- Theme colors

---

## Troubleshooting

### No AI Providers Available
- Check `.env` file has API keys
- Verify API keys are valid
- Restart the application

### Images Not Showing
- Check cache permissions
- Verify Flask server is running
- Clear browser cache

### Desktop Notifications Not Working
- Enable notifications in Windows Settings
- Check notification permissions for Python

---

## Data Location

- **Database**: `signals.db`
- **Cache**: `cache/` folder
- **Journal**: `journal/archives/` folder
- **Config**: `dashboard/config.py`

---

## Support

For issues or questions:
1. Check this guide
2. Review legal documents in `docs/`
3. Contact software provider

---

**Remember:** This is a tool to ASSIST your trading, not replace your judgment. Always do your own analysis!
