# Concepts Used 🧠

> A comprehensive reference of every technology, library, API, and design pattern used in Umer's Agent.

---

## 1. Core Agent Framework

### LangChain
- **What**: Open-source framework for building LLM-powered applications.
- **Used for**: Creating the `agent` object, defining tools, managing the message loop.
- **Key imports**: `create_agent`, `tool`, `HumanMessage`, `ToolMessage`
- **Docs**: https://docs.langchain.com

### LangChain Agents
- **Concept**: An agent is an LLM that can call external tools based on the user's query. It reasons about *which* tool to use, calls it, and integrates the result into its final response.
- **Pattern used**: ReAct-style (Reason + Act) agent loop.

### Middleware / `wrap_tool_call`
- **What**: Intercepts every tool call before execution.
- **Used for**: `human_approval` — prompts the user to approve/deny each tool call.
- **GUI adaptation**: `builtins.input` is monkey-patched to auto-return `"yes"`, so the GUI never blocks waiting for keyboard input.

---

## 2. LLM Provider

### MistralAI (`langchain-mistralai`)
- **Model**: `mistral-small-2506`
- **What**: A high-speed, cost-efficient LLM by Mistral AI.
- **Role**: The "brain" of the agent — decides which tool to call and generates the final answer.
- **API key**: `MISTRAL_API_KEY` in `.env`

---

## 3. External APIs & Tools

### OpenWeatherMap API
- **Endpoint**: `https://api.openweathermap.org/data/2.5/weather`
- **Method**: HTTP GET with params `{q: city, appid: key, units: metric}`
- **Returns**: Temperature (°C), weather description
- **Error handling**: Status code check + `requests.RequestException` catch

### Tavily Search API (`tavily-python`)
- **What**: AI-optimized web search API designed for LLM agents.
- **Used for**: Fetching the 5 latest news articles about a city.
- **Parameters**: `topic="news"`, `search_depth="advanced"`, `max_results=5`
- **Returns**: List of `{title, content, url}` objects

---

## 4. Frontend — Streamlit

### Streamlit
- **What**: Python framework for building interactive web apps with minimal code.
- **Version required**: ≥ 1.30
- **Key features used**:
  - `st.set_page_config()` — page meta
  - `st.markdown(unsafe_allow_html=True)` — embedded HTML/CSS
  - `st.text_input()` / `st.selectbox()` — form inputs
  - `st.button()` — CTA trigger
  - `st.spinner()` — loading indicator
  - `st.expander()` — collapsible history panel
  - `st.session_state` — client-side state persistence

### Streamlit Session State
- **Concept**: `st.session_state` persists Python objects across Streamlit re-runs (triggered by any user interaction).
- **Used for**: Storing `history` — a list of past queries and results.

---

## 5. Frontend — HTML/CSS Design Patterns

### Glassmorphism
- **Concept**: UI elements that look like frosted glass — semi-transparent backgrounds with `backdrop-filter: blur()`.
- **Implementation**: `background: rgba(255,255,255,0.04)` + `backdrop-filter: blur(24px)` + subtle border

### CSS Custom Properties (Variables)
- All design tokens (colors, fonts, transitions) defined as `--clr-*`, `--font-*`, `--radius-*` in `:root`.
- Enables consistent theming and easy future customization.

### CSS Keyframe Animations
| Animation | Effect |
|---|---|
| `gradientShift` | Slowly shifts the background gradient (12s loop) |
| `orbFloat` | Orbs gently float up and down (8s loop) |
| `fadeSlideDown` | Elements fade + slide in from above on page load |
| `resultReveal` | Result card fades + scales in from below |
| `pulse` | Status dot scales and fades rhythmically |

### Google Fonts API
- `Outfit` — display/heading font (weights: 300, 400, 600, 700, 900)
- `Inter` — body/UI font (weights: 300, 400, 500, 600)
- Loaded via `@import url('https://fonts.googleapis.com/...')`

### Gradient Text
- Technique: `background: linear-gradient(...)` + `-webkit-background-clip: text` + `-webkit-text-fill-color: transparent`
- Used on: Main title, sidebar logo

### CSS `clamp()` for Responsive Typography
- `font-size: clamp(2.4rem, 5vw, 3.8rem)` — fluidly scales between min/max based on viewport.

---

## 6. Python Patterns

### `importlib` — Dynamic Module Loading
- **Why**: The agent file is named `"automate agent.py"` (with a space), making it un-importable via normal `import` statement.
- **Solution**: `importlib.util.spec_from_file_location()` + `module_from_spec()` + `exec_module()`

### Monkey-Patching `builtins.input`
- **Why**: `human_approval` middleware calls `input()` to await user confirmation. In a GUI context, there's no terminal.
- **Solution**: Replace `builtins.input` with a function that always returns `"yes"` before the agent module is loaded.

### Environment Variables (`python-dotenv`)
- Loads `.env` file into `os.environ` at startup via `load_dotenv()`.
- Keeps API keys out of source code.

---

## 7. Architecture Pattern

### Separation of Concerns

| Layer | File | Responsibility |
|---|---|---|
| Agent Logic | `automate agent.py` | LLM, tools, middleware |
| Bridge | `agent_bridge.py` | Adapter — connects GUI to agent |
| Presentation | `gui.py` | Streamlit UI & UX |
| Styling | `styles/main_styles.css` | All visual design |
| Config | `.env` | API secrets |
| Docs | `*.md` | Human-readable documentation |

This pattern ensures the agent code is never tangled with UI code, and the UI is never tangled with styling — clean, maintainable, and extensible.
