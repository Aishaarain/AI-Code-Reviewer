# 🚀 Quick Start Guide

## 🎯 Choose Your Interface

### Option 1: Web Interface (Easiest!)
```cmd
run_webapp.cmd
```
**Opens in browser** → Paste PR URL → Click "Start Review" → Done!

### Option 2: Command Line
```cmd
.venv\Scripts\activate
py -m reviewer https://github.com/owner/repo/pull/123
```

---

## ⚡ First Time Setup (5 minutes)

### 1. Get API Keys

**Groq** (FREE!): https://console.groq.com/keys  
**GitHub**: https://github.com/settings/tokens

### 2. Add to `.env` file
```
GITHUB_TOKEN=ghp_your_token_here
GROQ_API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

### 3. Done!
That's it. Now run the app.

---

## 📝 Common Commands

### Web App
```cmd
run_webapp.cmd                    # Start web interface
```

### Command Line
```cmd
.venv\Scripts\activate            # Activate environment

py -m reviewer <PR_URL>           # Dry-run (print to console)
py -m reviewer <PR_URL> --post    # Post review to GitHub

py check_config.py                # Verify your setup
py test_real_pr.py                # Test on a real PR

pytest tests/ -v                  # Run all tests
```

---

## 🎨 Web Interface Features

- ✅ Visual progress bar
- ✅ Real-time agent status
- ✅ Bug/Security/Style counters
- ✅ Formatted Markdown output
- ✅ Download review button
- ✅ API key validation
- ✅ Error messages

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web interface |
| `run_webapp.cmd` | Quick launcher (Windows) |
| `.env` | Your API keys (NEVER commit!) |
| `reviewer/` | Core code (agents, graph, etc.) |
| `tests/` | Unit tests |

---

## 🐛 Quick Troubleshooting

**"Configuration Error"**
→ Check `.env` file has valid keys

**"Module not found"**
→ Run: `pip install -e ".[dev]"`

**Web app won't start**
→ Run: `pip install streamlit`

**404 Error (PR not found)**
→ Check the PR URL is correct and public

---

## 💡 Pro Tips

1. **Start with dry-run** - Test without posting first
2. **Use small PRs** - Easier to see what agents found
3. **Check the logs** - Agents print what they're doing
4. **Customize prompts** - Edit `reviewer/prompts/*.md`
5. **Deploy the web app** - Share with your team!

---

## 📚 More Help

- **Web App Guide**: [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
- **Detailed Usage**: [USAGE.md](USAGE.md)
- **Project Summary**: [WEB_APP_SUMMARY.md](WEB_APP_SUMMARY.md)

---

## 🎉 You're Ready!

### To start reviewing:
```cmd
run_webapp.cmd
```

That's it! Open your browser, paste a PR URL, and watch the AI agents work! 🚀
