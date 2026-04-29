# 🛡️ AI Smart Home Security Assistant

An intelligent chatbot that helps users monitor, manage, and secure their smart home security system. Built with Flask, Google Gemini AI, and a premium dark-themed web interface.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange?logo=google)

## ✨ Features

- **AI-Powered Conversations** — Google Gemini processes natural language queries about home security
- **Smart Home Simulation** — Control doors, cameras, alarms, motion sensors, and lights
- **Intent Detection** — Automatically classifies messages as commands, queries, alerts, or troubleshooting
- **Emergency Response** — Urgent, actionable advice during security alerts
- **Real-Time Dashboard** — Visual status of all home devices with live updates
- **Security Alerts** — Automatic vulnerability detection (e.g., door unlocked + alarm off)
- **Quick Actions** — One-click buttons for common security commands
- **Dark Theme UI** — Premium, modern interface with animations

## 🏗️ Architecture

```
User Message → Intent Detection → State Check → AI Processing → Response
                    ↓
              COMMAND → Update State → Confirm
              QUERY → AI + Context → Answer
              ALERT → AI + Urgency → Safety Steps
              TROUBLESHOOT → AI → Step-by-Step Fix
```

## 📁 Project Structure

```
├── app.py                 # Flask server & API routes
├── chatbot_logic.py       # AI response orchestration
├── intent_detector.py     # Message classification engine
├── state_manager.py       # Smart home state simulation
├── config.py              # System prompt & settings
├── templates/
│   └── index.html         # Chat UI
├── static/
│   ├── css/style.css      # Dark theme styling
│   ├── js/chat.js         # Frontend chat logic
│   └── images/logo.png    # App logo
├── requirements.txt       # Python dependencies
└── render.yaml            # Deployment config
```

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get free key](https://aistudio.google.com/apikey))

### Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-smart-home-security.git
cd ai-smart-home-security

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API key
# Edit .env file and add: GEMINI_API_KEY=your_key_here

# Run the server
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🌐 Deployment (Render.com)

1. Push code to GitHub
2. Sign up at [render.com](https://render.com)
3. Create **New → Web Service** → connect your repo
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `gunicorn app:app`
6. Add environment variable: `GEMINI_API_KEY=your_key`
7. Deploy!

## 🤖 Chatbot Capabilities

| Intent | Example | Response |
|---|---|---|
| **Command** | "Lock the door" | Updates device state + confirms |
| **Query** | "Is my home safe?" | AI analysis based on current state |
| **Alert** | "Someone is outside" | Urgent safety steps + emergency contacts |
| **Troubleshoot** | "Camera not working" | Step-by-step fix guide |
| **Greeting** | "Hello" | Welcome message + status summary |

## 🛠️ Tech Stack

- **Backend:** Python 3.14, Flask 3.1
- **AI Engine:** Google Gemini 2.5 Flash
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Fonts:** Inter (Google Fonts)
- **Deployment:** Render.com + Gunicorn

## 📝 License

This project is built for educational purposes (LPU B.Tech Project).
