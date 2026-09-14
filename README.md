[README.md](https://github.com/user-attachments/files/32191239/README.md)
# Umer's Agent 🤖

> **AI-Powered City Intelligence System** — Ask about weather or the latest news for any city on Earth.

---

## 📖 Overview

**Umer's Agent** is an AI agent built with LangChain and MistralAI that:

- Accepts a natural-language query (city name + intent).
- Decides autonomously whether to call the **weather tool** (OpenWeatherMap) or the **news tool** (Tavily Search).
- Returns a structured, human-readable answer.

The Streamlit frontend wraps the agent in a beautiful, interactive web UI without changing any of the original agent logic.

---

## 📁 Project Structure

```
Agent/
├── automate agent.py      — Original agent (LangChain + MistralAI + tools)
├── agent_bridge.py        — Thin adapter: exposes run_agent() to the GUI
├── gui.py                 — Streamlit web app entry-point
├── styles/
│   └── main_styles.css    — Premium dark-theme CSS (glassmorphism + animations)
├── .env                   — API keys (OpenWeather, Mistral, Tavily)
├── requirement.txt        — Python dependencies
├── README.md              — This file
├── execution_plan.md      — Step-by-step execution & run guide
├── gui_plan.md            — UI/UX design plan & wireframe description
└── concepts_used.md       — Technologies & design patterns reference
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9+ |
| pip / venv | latest |
| Streamlit | ≥ 1.30 |

---

## 🔑 API Keys Required

Add the following to your `.env` file:

```env
OPENWEATHER_API_KEY=your_openweather_key
MISTRAL_API_KEY=your_mistral_key
TAVILY_API_KEY=your_tavily_key
```

---

## 🚀 Setup & Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirement.txt
```

### 3. Launch the web app

```bash
streamlit run gui.py
```

The app will open automatically at **http://localhost:8501**.

---

## 🛠️ Tools Used by the Agent

| Tool | API | Purpose |
|---|---|---|
| `get_weather` | OpenWeatherMap | Current temperature & conditions |
| `get_latest_news` | Tavily Search | Top 5 recent news articles |

---

## 📸 Features

- 🌑 **Dark glassmorphism UI** with animated gradient backgrounds
- 🤖 **AI decides** which tool to use based on your query
- 🌦️ **Weather card** with teal accent styling
- 📰 **News card** with coral accent styling
- 🕘 **Query history** panel (last 5 results)
- 📱 **Responsive** design for any screen size

---

## ⚠️ Important Notes

1. The original `automate agent.py` is **never modified** by the GUI.
2. The `human_approval` middleware is auto-approved in GUI mode (no stdin prompt needed).
3. All API keys must be present in `.env` before launching.
