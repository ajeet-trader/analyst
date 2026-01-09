# AI Trading Analyst

**A modern, AI-powered trading signal assistant with web dashboard, signal logging, and desktop notifications.**

## Features

- 🤖 **AI Signal Analysis** - Multi-provider (Groq, HuggingFace, Together AI)
- 📊 **Web Dashboard** - Real-time signal display, history, win/loss tracking
- 🔔 **Desktop Notifications** - Windows toast alerts on new signals
- ⏱️ **Countdown Timer** - Signal expiry tracking
- 📈 **Pattern Recognition** - Candlestick pattern detection
- 🎯 **Multi-Timeframe** - Analyze 1m, 2m, 5m charts together
- 📝 **Signal Logging** - CSV export of all signals

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API keys
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python main.py
```

## Hotkeys

| Key | Action |
|-----|--------|
| `aa` | Capture current window |
| `c` | Analyze captured charts |
| `v` | View cache folder |
| `x` | Clear cached images |
| `q` | Quit application |

## API Keys (Free)

Get free API keys:
- **Groq**: https://console.groq.com
- **HuggingFace**: https://huggingface.co/settings/tokens
- **Together AI**: https://api.together.xyz

## Requirements

- Python 3.10+
- Windows 10/11

## License

MIT License - See LICENSE file

## Disclaimer

⚠️ **Not financial advice.** Use at your own risk. No profit guarantees.
