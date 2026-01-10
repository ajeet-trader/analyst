# Privacy Policy

**Last Updated:** January 10, 2026

## Overview

AI Trading Analyst is designed with privacy in mind. We believe your trading data should stay private.

## Data Collection

### What We DON'T Collect

✗ **Trading History** - Not collected or transmitted  
✗ **Personal Information** - No registration required  
✗ **Financial Data** - No bank or broker information  
✗ **Browsing Activity** - No tracking cookies  
✗ **Location Data** - Not collected  

### What We DO Store (Locally Only)

✓ **Signals** - Stored in local SQLite database  
✓ **Chart Screenshots** - Saved to local `cache/` and `journal/` folders  
✓ **Win/Loss Results** - Stored locally for analytics  
✓ **User Notes** - Saved locally in journal  
✓ **API Keys** - Stored locally in `.env` file  

**Important:** All data is stored on YOUR computer only. We have no access to your data.

## Third-Party Services

The software connects to external AI providers:
- **Groq** - For AI analysis
- **HuggingFace** - For AI analysis
- **Together AI** - For AI analysis

### What Gets Sent to AI Providers

- Chart screenshot images (temporary, for analysis)
- No personal information
- No trading account details
- No financial information

### Third-Party Privacy Policies

You should review the privacy policies of:
- Groq: https://groq.com/privacy-policy
- HuggingFace: https://huggingface.co/privacy
- Together AI: https://www.together.ai/privacy

## Data Security

### Your Responsibility

- Secure your device and files
- Protect your `.env` file with API keys
- Back up your data regularly
- Use strong passwords for trading accounts

### Our Measures

- No data transmission to our servers
- No cloud storage
- Local-only database
- No external analytics

## Data Deletion

To delete your data:
1. Delete the `signals.db` file
2. Delete the `cache/` folder
3. Delete the `journal/` folder
4. Uninstall the software

## Children's Privacy

This software is not intended for users under 18 years of age.

## Updates to Privacy Policy

We may update this policy. Check the "Last Updated" date above.

## Questions

For privacy questions, contact the software provider.

---

**Summary:** Your trading data stays on your computer. We don't collect, store, or transmit your personal or trading information.
