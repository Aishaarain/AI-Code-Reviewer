# 🎨 Streamlit Web Interface Guide

## Quick Start

### Run the Web App

**Windows:**
```cmd
.venv\Scripts\activate
streamlit run app.py
```

**Mac/Linux:**
```bash
source .venv/bin/activate
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Features

### 🎯 Easy to Use
- Just paste any GitHub PR URL
- Click "Start Review" and watch the agents work
- See real-time progress and status updates

### 📊 Visual Dashboard
- See findings count for each agent (Bug, Security, Style)
- Real-time progress bar
- Clean, organized review output

### ⚡ Fast & Interactive
- Parallel agent execution (3 agents at once!)
- Live status updates
- Download review as Markdown

### 🔒 Safe Testing
- Checkbox to control posting to GitHub
- Dry-run mode by default (just shows review)
- Check the "Post review to GitHub" box only when ready

---

## What You'll See

1. **Configuration Check** (sidebar)
   - Shows if your API keys are valid
   - Displays current model and keys (masked)

2. **PR Input Area**
   - Text box for GitHub PR URL
   - Checkbox for posting to GitHub
   - Big "Start Review" button

3. **Review Process** (when you click Start)
   - **Step 1**: Fetching PR data (title, author, files)
   - **Step 2**: Three agents analyze in parallel
     - 🐛 Bug Agent
     - 🔒 Security Agent  
     - ✨ Style Agent
   - **Step 3**: Synthesizer combines findings
   - **Step 4**: (Optional) Post to GitHub
   - **Step 5**: Display final review

4. **Results**
   - Stats counters (bug/security/style counts)
   - Full markdown review
   - Download button to save review

---

## Tips

### First Time Using?
1. Start with a small, public PR
2. Leave "Post to GitHub" unchecked
3. Review the output before posting

### Testing Different PRs
- Try PRs with different types of code
- See how agents respond to bugs vs clean code
- Compare reviews across languages

### Customizing
Edit `app.py` to:
- Change colors (CSS at top)
- Add more stats/charts
- Customize the layout

---

## Keyboard Shortcuts

- `Ctrl + R` or `R` - Rerun the app
- `Ctrl + C` (in terminal) - Stop the server

---

## Troubleshooting

**"Configuration Error"**
- Make sure `.env` file has valid keys
- Check sidebar for error details

**"Module not found"**
- Make sure virtual environment is activated
- Run: `pip install -e ".[dev]"`

**App won't start**
- Check if port 8501 is available
- Try: `streamlit run app.py --server.port 8502`

**Slow performance**
- Large PRs take longer
- Groq is usually fast (<10 seconds)
- Check your internet connection

---

## Advanced: Deploy the App

### Deploy to Streamlit Cloud (Free!)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Streamlit Cloud:
   ```
   GITHUB_TOKEN = "your_token"
   GROQ_API_KEY = "your_key"
   MODEL = "llama-3.3-70b-versatile"
   ```
5. Deploy!

### Run on a Server

```bash
# Install
pip install -e ".[dev]"

# Run with public access
streamlit run app.py --server.address 0.0.0.0 --server.port 8080
```

---

## Comparison: CLI vs Web

| Feature | CLI (`py -m reviewer`) | Web (`streamlit run app.py`) |
|---------|----------------------|----------------------------|
| Interface | Terminal | Browser |
| Progress | Text output | Visual progress bar |
| Stats | Printed summary | Live counters |
| Review display | Plain text | Formatted Markdown |
| Ease of use | Technical | User-friendly |
| Best for | Automation, CI/CD | Interactive use, demos |

**Both interfaces use the same backend!** Choose based on your needs.

---

## Next Steps

- Try the app on real PRs
- Share it with your team
- Customize the UI to match your brand
- Deploy to Streamlit Cloud

Enjoy your beautiful code reviewer! 🚀
