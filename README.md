# 📧 Email AI Processor - Setup Guide

An automated email processor that uses Google Gemini AI to categorize incoming mail and draft professional responses.

## 📁 Project Structure
```text
email-processor/
├── .env                 # API keys & passwords (SECRET - DO NOT SHARE)
├── .gitignore           # Crucial: Keeps your .env off GitHub
├── email_processor.py   # Main logic (uses google-genai)
├── config.py            # Configuration loader (uses python-dotenv)
├── run.py               # Entry point for the script
├── requirements.txt     # Dependencies
└── README.md            # This file
```
---

## 🚀 Quick Setup (5 minutes)
### Step 1: Install Python Packages
Google has migrated to a new library. Use the following:
```bash
pip install google-genai python-dotenv
```

### Step 2: Get Gmail App Password
1. Go to your Google Account.
2. Enable 2-Step Verification.
3. Search for App Passwords.
4. Create one named "Email Processor" and copy the 16-character code.

### Step 3: Get Gemini API Key
1. Go to Google AI Studio.
2. Create a new API key.
3. Important: If your key is ever leaked to GitHub, Google will disable it automatically.

### Step 4: Configure (.env file)
DO NOT edit config.py directly with your keys. Create a file named .env in the root folder:
```text
GEMINI_API_KEY="your_api_key_here"
EMAIL_ADDRESS="your_email@gmail.com"
GMAIL_APP_PASS="your_16_char_password"
```
---

## 🔒 Security Warning
Never commit your .env file to GitHub. If you accidentally commit your keys:
1. Delete the API key in Google AI Studio immediately.
2. Revoke the Gmail App Password.
3. Run git rm --cached .env and force push a fix.

---
## 📧 What It Does
- Smart Filtering: Only processes UNSEEN (unread) emails.
- AI Categorization: Uses Gemini 2.0 Flash to tag emails as URGENT, SPAM, etc.
- Fallback Logic: If the AI hits a quota limit, the script saves a generic "Thank You" draft so you don't lose the communication.
- Local Drafts: Saves a .txt file for every email so you can review before sending.

---
## ⚙️ Quota & Rate Limits (Free Tier)
As of 2026, the Gemini Free Tier has strict limits:
- Rate Limit: ~5-15 requests per minute.
- Daily Limit: ~100-150 requests per day.Error 429: If you see RESOURCE_EXHAUSTED, the script will wait and retry or save a fallback draft.

---
## 🔧 Troubleshooting

If you encounter issues during setup or execution, refer to the table below:

| Error | Solution |
|------|----------|
| **429 Resource Exhausted** | You have hit the free tier limit. Increase `CHECK_INTERVAL` to `600` (10 minutes). |
| **403 Permission Denied** | Your API key was leaked and disabled by Google. Generate a new key in Google AI Studio. |
| **ImportError: genai** | Run `pip uninstall google-generativeai` then `pip install google-genai`. |
| **AttributeError: 'model'** | Ensure you are using `self.model` in your code (e.g., in `__init__`), not just `model`. |

---
## 📝 Usage
Run Once:
```bash
python run.py
```
Run Continuously: The script checks your inbox at a set interval (default 300s) to respect AI rate limits.

