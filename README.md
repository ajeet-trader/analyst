# AI Trading Analyst

**AI-Powered Trading Signal Analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ DISCLAIMER

**THIS SOFTWARE IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY**

Trading involves substantial risk of loss. This is NOT financial advice. You are solely responsible for your trading decisions. See [DISCLAIMER.md](docs/DISCLAIMER.md) for full details.

---

## Features

✨ **AI Analysis** - Multiple free AI providers (Groq, HuggingFace, Together AI)  
📊 **Multi-Timeframe** - Analyze 1m, 2m, 5m, 15m charts simultaneously  
🎯 **Pattern Recognition** - Detects candlestick patterns and trends  
📈 **Analytics Dashboard** - Performance tracking by asset, pattern, and time  
📔 **Automatic Journal** - Archives every trade with charts and analysis  
🔔 **Desktop Notifications** - Instant signal alerts  
🗄️ **Local Database** - All data stays on your computer  
⚙️ **Config-Driven** - Customize everything via `dashboard/config.py`  

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup API Keys
Copy `.env.example` to `.env` and add ONE API key (at minimum):
```env
GROQ_API_KEY=your_key_here
```

Get free keys:
- [Groq](https://console.groq.com)
- [HuggingFace](https://huggingface.co/settings/tokens)
- [Together AI](https://api.together.xyz)

### 3. Run
```bash
python main.py
```

Dashboard opens at: http://127.0.0.1:5000

---

## Usage

1. **Capture** - Press `aa` to screenshot 3 charts
2. **Analyze** - Press `c` to get AI signal (2-4s)
3. **Trade** - Review signal and make your decision
4. **Record** - Click WIN/LOSS after trade expires
5. **Review** - Check Analytics and Journal pages

---

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete usage instructions
- [Terms of Service](docs/TERMS.md) - Legal terms
- [Privacy Policy](docs/PRIVACY.md) - Data handling
- [Disclaimer](docs/DISCLAIMER.md) - Risk warnings

---

## Configuration

Edit `dashboard/config.py` to customize:
- AI providers and priorities
- Dashboard colors and theme
- Data limits and timeouts
- Feature flags
- Notification settings

---

## Tech Stack

- **Backend**: Python, Flask, SocketIO
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Database**: SQLite
- **AI**: Groq, HuggingFace, Together AI
- **Notifications**: winotify

---

## License

MIT License - See [LICENSE](LICENSE) file

**Additional Trading Disclaimer**: This software provides signals for informational purposes only. Not financial advice. Use at your own risk.

---

## Support

**Before asking for support:**
1. Read the [User Guide](docs/USER_GUIDE.md)
2. Check the [Disclaimer](docs/DISCLAIMER.md)
3. Review configuration in `dashboard/config.py`

---

**Remember: AI is a tool, not a crystal ball. Always do your own research!**
