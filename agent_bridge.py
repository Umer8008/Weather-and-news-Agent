"""
agent_bridge.py
================
Thin adapter between the Streamlit GUI and the original agent logic.

Rules:
  - Does NOT modify any logic in 'automate agent.py'.
  - Provides a single public function: run_agent(user_input) -> str
  - Auto-approves tool calls so the GUI works without stdin prompts.
"""

import importlib.util
import os
import sys
from pathlib import Path

# Automatically bridge .venv site-packages if running from an external Python
_venv_site = Path(__file__).parent / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

from langchain_core.messages import ToolMessage

# ------------------------------------------------------------------ #
#  Patch `input` and `rich.print` BEFORE importing automate agent.py  #
#  - Loop prompt returns "exit" so the module doesn't block in loop   #
#  - Tool approval prompt returns "yes" so tool calls are auto-approved#
#  - rich.print avoids Windows cp1252 encoding crashes on emojis      #
# ------------------------------------------------------------------ #

import builtins
import rich

def _smart_input(prompt: str = "") -> str:
    prompt_str = str(prompt).lower()
    if "allow this tool call" in prompt_str or "yes/no" in prompt_str:
        return "yes"
    # When automate agent.py executes its top-level interactive while True loop:
    return "exit"

builtins.input = _smart_input

# Protect against Windows cp1252 encoding crashes on rich prints
_orig_rich_print = rich.print
def _safe_rich_print(*args, **kwargs):
    try:
        _orig_rich_print(*args, **kwargs)
    except Exception:
        pass
rich.print = _safe_rich_print


# ------------------------------------------------------------------ #
#  Dynamically load 'automate agent.py' (space in filename).         #
# ------------------------------------------------------------------ #

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENT_FILE = os.path.join(_BASE_DIR, "automate agent.py")

spec = importlib.util.spec_from_file_location("automate_agent", _AGENT_FILE)
_agent_module = importlib.util.module_from_spec(spec)
sys.modules["automate_agent"] = _agent_module
spec.loader.exec_module(_agent_module)

# Grab the compiled agent object from the module
_agent = _agent_module.agent


# ------------------------------------------------------------------ #
#  Public API                                                         #
# ------------------------------------------------------------------ #

def run_agent(user_input: str) -> str:
    """
    Send *user_input* to the LangChain agent and return the final text reply.

    Parameters
    ----------
    user_input : str
        Natural-language query from the Streamlit GUI (city + intent).

    Returns
    -------
    str
        The agent's final text response.
    """
    result = _agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })
    return result["messages"][-1].content
