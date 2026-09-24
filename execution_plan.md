# Execution Plan 📋


> Step-by-step breakdown of how Umer's Agent processes a request from user click to final response.

---

## Phase 1 — Application Startup

```
streamlit run gui.py
        │
        ▼
 st.set_page_config()          ← Sets page title, icon, layout
        │
        ▼
 _inject_css()                 ← Reads styles/main_styles.css, injects via st.markdown()
        │
        ▼
 Sidebar renders               ← Tips, status badge, credits
        │
        ▼
 Hero header renders           ← Animated title + subtitle
        │
        ▼
 Input card renders            ← City text input + query type selectbox + button
        │
        ▼
 Empty state renders           ← "Ready to Explore" placeholder card
```

---

## Phase 2 — User Input

```
User types city name           ← e.g. "Karachi"
        │
User selects query type        ← e.g. "🌦️ Weather Update"
        │
User clicks "Ask the Agent"
        │
        ▼
 _build_prompt(city, query_type)
   ├─ "Weather" → "What is the current weather in Lahore?"
   ├─ "News"    → "What is the latest news in Lahore?"
   └─ "Agent"   → "Give me information about Lahore — either weather or news."
```

---

## Phase 3 — Agent Bridge Invocation

```
from agent_bridge import run_agent
        │
        ▼
 agent_bridge.py loads on first import:
   1. Monkey-patches builtins.input → auto-returns "yes"
      (so human_approval middleware never blocks stdin)
   2. Dynamically loads "automate agent.py" via importlib
   3. Extracts the compiled `agent` LangChain object
        │
        ▼
 run_agent(prompt) called
   └── agent.invoke({"messages": [{"role":"user","content": prompt}]})
```

---

## Phase 4 — LangChain Agent Execution (inside automate agent.py)

```
MistralAI LLM receives prompt
        │
        ▼
 LLM decides which tool to call:
   ├─ get_weather(city)      → OpenWeatherMap REST API call
   │                           Returns: "The current weather in X is Y°C with Z."
   │
   └─ get_latest_news(city)  → Tavily Search API call
                               Returns: Numbered list of 5 articles with URLs
        │
        ▼
 human_approval middleware fires:
   └── builtins.input("Allow this tool call?") → returns "yes" automatically
        │
        ▼
 Tool executes → result returned to LLM
        │
        ▼
 LLM generates final natural-language response
        │
        ▼
 result["messages"][-1].content  returned to run_agent()
```

---

## Phase 5 — Response Rendering

```
agent_result string returned to gui.py
        │
        ▼
 _detect_kind(agent_result)
   ├─ Contains "°C" / "temperature"  → kind = "weather"
   ├─ Contains "Source:" / "1. "    → kind = "news"
   └─ Otherwise                     → kind = "general"
        │
        ▼
 Result stored in st.session_state.history[0]
        │
        ▼
 HTML result-card rendered with:
   ├─ Icon (🌤️ / 📰 / 🤖)
   ├─ Colored label (teal / coral / purple)
   ├─ Styled divider
   └─ Formatted response body
        │
        ▼
 Previous queries stored in expander (history[1:])
```

---

## Phase 6 — Error Handling

| Scenario | Behaviour |
|---|---|
| Empty city input | Warning card shown, no API call made |
| API key missing | Error message from tool returned & displayed |
| Network failure | `requests.RequestException` caught, shown in card |
| Agent exception | `except Exception` in gui.py catches it, shows error card |

---

## Run Command Quick Reference

```bash
# First time setup
pip install -r requirement.txt

# Launch GUI
streamlit run gui.py

# Access at
http://localhost:8501
```
