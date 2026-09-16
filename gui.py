#.venv\Scripts\python.exe -m streamlit run gui.py --server.port 8502

"""
gui.py
=======
Streamlit frontend for **Umer's Agent** — City Intelligence System.

Run with:
    streamlit run gui.py

Rules:
  - Original agent code (automate agent.py) is NEVER modified.
  - All agent invocations go through agent_bridge.run_agent().
  - Embedded HTML/CSS loaded from styles/main_styles.css.
"""


import os
import re
import sys
from pathlib import Path

# Ensure local .venv site-packages is in sys.path even when run with global streamlit
_venv_site = Path(__file__).parent / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

import streamlit as st

# ================================================================== #
#  PAGE CONFIG  (must be the first Streamlit call)                   #
# ================================================================== #

st.set_page_config(
    page_title="Umer's Agent — City Intelligence",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Umer's Agent — AI-powered city intelligence (weather & news)."
    },
)


# ================================================================== #
#  LOAD & INJECT CSS                                                  #
# ================================================================== #

def _inject_css() -> None:
    css_path = Path(__file__).parent / "styles" / "main_styles.css"
    if css_path.exists():
        css_text = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

_inject_css()


# ================================================================== #
#  BACKGROUND ORBS  (decorative blobs via HTML)                      #
# ================================================================== #

st.markdown(
    """
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
    """,
    unsafe_allow_html=True,
)


# ================================================================== #
#  SIDEBAR                                                            #
# ================================================================== #

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">🤖 Umer's Agent</div>
        <div class="sidebar-tagline">City Intelligence System</div>
        <hr class="styled-divider"/>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 How to Use", unsafe_allow_html=False)

    st.markdown(
        """
        <div class="tip-card">
          <span class="emoji">🌆</span>
          Type any city name — e.g. <strong>Lahore</strong>, <strong>London</strong>, <strong>Tokyo</strong>.
        </div>
        <div class="tip-card">
          <span class="emoji">🌦️</span>
          Ask for <strong>weather</strong> to get live temperature &amp; conditions.
        </div>
        <div class="tip-card">
          <span class="emoji">📰</span>
          Ask for <strong>news</strong> to get the 5 latest stories from that city.
        </div>
        <div class="tip-card">
          <span class="emoji">🧠</span>
          Or just describe what you want — the AI agent figures it out!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr class='styled-divider'/>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="status-badge">
          <div class="status-dot"></div>
          Agent Online
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.caption("Powered by MistralAI · OpenWeather · Tavily")


# ================================================================== #
#  HERO HEADER                                                        #
# ================================================================== #

st.markdown(
    """
    <div class="hero-wrapper">
      <div class="hero-badge">✦ AI-Powered Intelligence</div>
      <h1 class="hero-title">Umer's Agent</h1>
      <p class="hero-subtitle">
        Ask about <em>weather</em> or <em>news</em> for any city on Earth — the AI decides which tool to use.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ================================================================== #
#  INPUT CARD                                                         #
# ================================================================== #

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    city = st.text_input(
        "🏙️ City Name",
        placeholder="e.g. Karachi, Paris, Dubai…",
        key="city_input",
    )

with col2:
    query_type = st.selectbox(
        "🔍 Query Type",
        options=[
            "🧠 Let Agent Decide",
            "🌦️ Weather Update",
            "📰 Latest News",
        ],
        key="query_type",
    )

# Build the user prompt from inputs
def _build_prompt(city: str, query_type: str) -> str:
    if not city.strip():
        return ""
    qt = query_type.strip()
    if "Weather" in qt:
        return f"What is the current weather in {city}?"
    elif "News" in qt:
        return f"What is the latest news in {city}?"
    else:
        return f"Give me information about {city} — either weather or news."

run_btn = st.button("🚀 Ask the Agent", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)  # close glass-card


# ================================================================== #
#  SESSION STATE                                                      #
# ================================================================== #

if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts: {query, result, kind}


# ================================================================== #
#  AGENT INVOCATION                                                   #
# ================================================================== #

def _detect_kind(result_text: str) -> str:
    """Heuristic: detect whether result is weather, news, or general."""
    lower = result_text.lower()
    if any(kw in lower for kw in ["°c", "temperature", "humidity", "weather", "wind", "feels like"]):
        return "weather"
    if any(kw in lower for kw in ["news", "source:", "http", "headline", "1.", "2.", "3."]):
        return "news"
    return "general"


if run_btn:
    if not city.strip():
        st.markdown(
            """
            <div class="result-card general">
              <div class="result-icon">⚠️</div>
              <div class="result-label general">Input Required</div>
              <div class="result-body">Please enter a city name before submitting.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        prompt = _build_prompt(city.strip(), query_type)

        with st.spinner("🤖 Agent is thinking…"):
            try:
                from agent_bridge import run_agent
                agent_result = run_agent(prompt)
            except Exception as exc:
                agent_result = f"❌ Error communicating with the agent:\n\n{exc}"

        kind = _detect_kind(agent_result)

        # Store in history
        st.session_state.history.insert(0, {
            "query": prompt,
            "result": agent_result,
            "kind": kind,
            "city": city.strip(),
        })


# ================================================================== #
#  DISPLAY RESULTS                                                    #
# ================================================================== #

def _format_result_body(text: str) -> str:
    """Format agent output into clean HTML: remove raw asterisks, convert markdown bold, and linkify URLs."""
    if not text:
        return ""
    # Escape raw HTML brackets
    formatted = text.replace("<", "&lt;").replace(">", "&gt;")
    # Convert markdown bold **text** to styled HTML <strong> (removes asterisks)
    formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #ffffff; font-weight: 600;">\1</strong>', formatted)
    # Remove any remaining raw asterisks (* or ***)
    formatted = formatted.replace("**", "").replace("*", "")
    # Make URLs clickable
    url_pattern = r'(https?://[^\s<]+)'
    formatted = re.sub(url_pattern, r'<a href="\1" target="_blank" style="color:var(--clr-weather); text-decoration:underline;">\1</a>', formatted)
    return formatted


if st.session_state.history:
    latest = st.session_state.history[0]

    ICON_MAP = {"weather": "🌤️", "news": "📰", "general": "🤖"}
    LABEL_MAP = {"weather": "Weather Update", "news": "Latest News", "general": "Agent Response"}

    icon  = ICON_MAP[latest["kind"]]
    label = LABEL_MAP[latest["kind"]]
    kind  = latest["kind"]
    body  = _format_result_body(latest["result"])

    st.markdown(
        f"""
        <div class="result-card {kind}">
          <div class="result-icon">{icon}</div>
          <div class="result-label {kind}">{label} — {latest["city"]}</div>
          <hr class="styled-divider"/>
          <div class="result-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Conversation History ----------------------------------------
    if len(st.session_state.history) > 1:
        st.markdown("<br/>", unsafe_allow_html=True)
        with st.expander("🕘 Previous Queries", expanded=False):
            for entry in st.session_state.history[1:]:
                e_icon  = ICON_MAP[entry["kind"]]
                e_label = LABEL_MAP[entry["kind"]]
                e_body  = _format_result_body(entry["result"])
                st.markdown(
                    f"""
                    <div class="result-card {entry['kind']}" style="margin-top:0.8rem;">
                      <div class="result-icon" style="font-size:1.4rem">{e_icon}</div>
                      <div class="result-label {entry['kind']}">{e_label} — {entry['city']}</div>
                      <div class="result-body" style="font-size:0.9rem">{e_body}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ================================================================== #
#  EMPTY STATE  (first load, no queries yet)                          #
# ================================================================== #

else:
    st.markdown(
        """
        <div class="result-card general" style="text-align:center; padding: 3rem 2rem;">
          <div class="result-icon" style="font-size:3.5rem">🌍</div>
          <div class="result-label general" style="font-size:1rem; margin-top:0.5rem;">
            Ready to Explore
          </div>
          <div class="result-body" style="color: rgba(232,232,240,0.5); margin-top:0.5rem;">
            Enter a city name above and hit <strong>Ask the Agent</strong> to get started.<br/>
            The AI will automatically decide whether to fetch weather or news.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================== #
#  FOOTER                                                             #
# ================================================================== #

st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; color: rgba(232,232,240,0.25); font-size:0.78rem; font-family:'Outfit',sans-serif;">
      Umer's Agent &nbsp;·&nbsp; Built with Streamlit &amp; LangChain &nbsp;·&nbsp; 2026
    </div>
    """,
    unsafe_allow_html=True,
)
