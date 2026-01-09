# Project Vision

## Current State (v1.0)
- Desktop app with web dashboard
- AI signal generation (Groq primary)
- Desktop notifications
- Win/loss tracking
- Signal history (session only)

## Short-term Goals (v1.5)
- [ ] SQLite database for persistence
- [ ] Signal history survives restart
- [ ] Enhanced analytics dashboard
- [ ] Automatic trading journal
- [ ] Telegram notifications

## Long-term Vision (v2.0+)
- [ ] Cloud deployment (multi-user SaaS)
- [ ] Multiple market prompts (binary, forex, crypto)
- [ ] OHLCV data integration
- [ ] AI chart drawings
- [ ] Payment integration (subscription)
- [ ] n8n workflow integration
- [ ] User trade history import

## Architecture Principles
1. **Modular** - Each feature is a separate module
2. **Config-driven** - Settings in config.py, not hardcoded
3. **Fast** - Signal generation <3 seconds
4. **Fallback** - Multiple AI providers with auto-switch
5. **Open source first** - Use free/open tools

## Revenue Model
- Subscription-based SaaS
- Free tier: Limited signals/day
- Pro tier: Unlimited + journal + analytics
