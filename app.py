"""
URBANE — City Intelligence Agent
A Streamlit front-end for the LangChain + Groq + Tavily + OpenRouteService agent.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st


# Import our backend agent logic
from agent import build_agent


# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="City Intelligence Agent",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Design tokens / CSS — "night map" theme
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
    --ink: #0B1120;
    --panel: #131B2E;
    --panel-2: #182238;
    --line: #26314A;
    --beacon: #FFB454;
    --route: #4FD1C5;
    --text: #E7ECF5;
    --muted: #7C8AA6;
    --danger: #FF6B6B;
}

.stApp{
    background:
        radial-gradient(circle at 15% 0%, rgba(255,180,84,0.06), transparent 40%),
        radial-gradient(circle at 85% 20%, rgba(79,209,197,0.07), transparent 45%),
        var(--ink);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"]{
    background: var(--panel);
    border-right: 1px solid var(--line);
}

/* Hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* ---------- Header ---------- */
.urbane-header{
    display:flex;
    align-items:center;
    gap: 14px;
    padding: 6px 0 18px 0;
    border-bottom: 1px solid var(--line);
    margin-bottom: 22px;
}
.pin-wrap{
    position:relative;
    width:34px; height:34px;
    display:flex; align-items:center; justify-content:center;
}
.pin-dot{
    width:10px; height:10px; border-radius:50%;
    background: var(--beacon);
    box-shadow: 0 0 8px var(--beacon);
    z-index:2;
}
.pin-ring{
    position:absolute; width:34px; height:34px; border-radius:50%;
    border: 1.5px solid var(--beacon);
    opacity:0;
    animation: sweep 2.6s ease-out infinite;
}
@keyframes sweep{
    0%   { transform: scale(0.3); opacity: 0.9; }
    100% { transform: scale(1.6); opacity: 0; }
}
.urbane-title{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin:0;
}
.urbane-sub{
    color: var(--muted);
    font-size: 13px;
    margin-top: 2px;
}

/* ---------- Status dots (sidebar) ---------- */
.status-row{
    display:flex; align-items:center; gap:8px;
    font-size: 13px; color: var(--muted);
    margin: 2px 0 14px 2px;
}
.status-dot{
    width:8px; height:8px; border-radius:50%;
    background: var(--danger);
    box-shadow: 0 0 6px var(--danger);
}
.status-dot.on{ background: var(--route); box-shadow: 0 0 6px var(--route); }

/* ---------- Chips ---------- */
.chip-btn button{
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    color: var(--text) !important;
    border-radius: 999px !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease;
}
.chip-btn button:hover{
    border-color: var(--beacon) !important;
    color: var(--beacon) !important;
}

/* ---------- Chat bubbles ---------- */
.bubble-row{
    display:flex;
    margin: 10px 0;
    animation: rise 0.35s ease;
}
@keyframes rise{
    from { opacity:0; transform: translateY(8px); }
    to   { opacity:1; transform: translateY(0); }
}
.bubble{
    max-width: 74%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 14.5px;
    line-height: 1.55;
    border: 1px solid var(--line);
}
.bubble.user{
    margin-left:auto;
    background: linear-gradient(180deg, rgba(79,209,197,0.16), rgba(79,209,197,0.06));
    border-color: rgba(79,209,197,0.35);
    border-bottom-right-radius: 4px;
}
.bubble.assistant{
    margin-right:auto;
    background: var(--panel-2);
    border-bottom-left-radius: 4px;
}
.bubble-eyebrow{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
}

/* ---------- Readout cards (weather / route data) ---------- */
.readout{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    background: rgba(255,180,84,0.06);
    border: 1px dashed rgba(255,180,84,0.35);
    border-radius: 10px;
    padding: 8px 12px;
    margin-top: 8px;
    color: var(--beacon);
    display:inline-block;
}

/* ---------- Thinking indicator ---------- */
.thinking{
    display:flex; gap:5px; align-items:center; padding: 4px 0 4px 4px;
}
.thinking span{
    width:6px; height:6px; border-radius:50%;
    background: var(--muted);
    animation: blink 1.2s infinite ease-in-out;
}
.thinking span:nth-child(2){ animation-delay: 0.2s; }
.thinking span:nth-child(3){ animation-delay: 0.4s; }
@keyframes blink{
    0%, 80%, 100% { opacity: 0.25; }
    40% { opacity: 1; }
}

/* Chat input */
[data-testid="stChatInput"]{
    background: var(--panel) !important;
    border-top: 1px solid var(--line) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar — secure key entry
# --------------------------------------------------------------------------
def _dot(ok: bool) -> str:
    return f'<span class="status-dot{" on" if ok else ""}"></span>'


with st.sidebar:
    st.markdown(
        "<div style='font-family:Space Grotesk; font-weight:700; "
        "letter-spacing:0.05em; font-size:15px; margin-bottom:4px;'>CONNECTIONS</div>",
        unsafe_allow_html=True,
    )
    st.caption("Keys stay in this browser session only — never written to disk or sent anywhere but the provider you're calling.")

    groq_key = st.text_input("Groq API Key", type="password", value=st.session_state.get("groq_key", ""), placeholder="gsk_...")
    tavily_key = st.text_input("Tavily API Key", type="password", value=st.session_state.get("tavily_key", ""), placeholder="tvly-...")
    ors_key = st.text_input("OpenRouteService API Key", type="password", value=st.session_state.get("ors_key", ""), placeholder="eyJ...")

    st.session_state["groq_key"] = groq_key
    st.session_state["tavily_key"] = tavily_key
    st.session_state["ors_key"] = ors_key

    use_env_fallback = st.checkbox("Fall back to server .env if a field is blank", value=True)

    def resolved(key_val, env_name):
        if key_val:
            return key_val
        if use_env_fallback:
            return "no api key found"
        return ""

    final_groq = resolved(groq_key, "GROQ_API_KEY")
    final_tavily = resolved(tavily_key, "Tavily_API_KEY")
    final_ors = resolved(ors_key, "OpenRouteService_API")

    st.markdown(
        f"<div class='status-row'>{_dot(bool(final_groq))} Groq (reasoning)</div>"
        f"<div class='status-row'>{_dot(bool(final_tavily))} Tavily (search)</div>"
        f"<div class='status-row'>{_dot(bool(final_ors))} OpenRouteService (routing)</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.divider()
    st.caption("Model: llama-3.3-70b-versatile via Groq")


ready = bool(final_groq)  # Groq is the only hard requirement to run the agent at all

# Optional cache on building the agent to save overhead on standard runs
@st.cache_resource(show_spinner=False)
def get_cached_agent(g_key, t_key, o_key):
    return build_agent(g_key, t_key, o_key)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="urbane-header">
        <div class="pin-wrap">
            <div class="pin-ring"></div>
            <div class="pin-dot"></div>
        </div>
        <div>
            <p class="urbane-title">Urbane</p>
            <p class="urbane-sub">City Intelligence Agent — weather, news, and routes for any city</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not ready:
    st.info("Add your **Groq API key** in the sidebar to start chatting. Tavily and OpenRouteService keys unlock news and routing.")

# --------------------------------------------------------------------------
# Chat state
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Suggested prompt chips
if not st.session_state["messages"]:
    st.markdown("<div style='margin-bottom:8px; color:var(--muted); font-size:13px;'>Try asking:</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    chips = [
        ("☁️ Weather in Tokyo", "What's the weather like in Tokyo right now?"),
        ("📰 News in Paris", "What's the latest news in Paris?"),
        ("🧭 Route to Delhi", "Get me driving directions from Ahmedabad to Delhi."),
        ("🏛️ Explore Rome", "Tell me about tourist attractions and history in Rome."),
    ]
    for col, (label, prompt) in zip(cols, chips):
        with col:
            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
            if st.button(label, key=f"chip-{label}", use_container_width=True):
                st.session_state["pending_prompt"] = prompt
            st.markdown('</div>', unsafe_allow_html=True)

# Render history
for msg in st.session_state["messages"]:
    role = msg["role"]
    eyebrow = "You" if role == "user" else "Urbane"
    st.markdown(
        f"""
        <div class="bubble-row">
            <div class="bubble {role}">
                <div class="bubble-eyebrow">{eyebrow}</div>
                {msg["content"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------
# Input handling
# --------------------------------------------------------------------------
user_input = st.chat_input("Ask about weather, news, or routes for any city...", disabled=not ready)

pending = st.session_state.pop("pending_prompt", None)
query = pending or user_input

if query:
    if not ready:
        st.warning("Add a Groq API key in the sidebar first.")
    else:
        st.session_state["messages"].append({"role": "user", "content": query})
        st.markdown(
            f"""
            <div class="bubble-row">
                <div class="bubble user">
                    <div class="bubble-eyebrow">You</div>
                    {query}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        placeholder = st.empty()
        placeholder.markdown(
            """
            <div class="bubble-row">
                <div class="bubble assistant">
                    <div class="bubble-eyebrow">Urbane</div>
                    <div class="thinking"><span></span><span></span><span></span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            agent = get_cached_agent(final_groq, final_tavily, final_ors)
            response = agent.invoke({"messages": [{"role": "user", "content": query}]})
            answer = response["messages"][-1].content
        except Exception as e:
            answer = f"Something went wrong reaching a tool or model: `{e}`"

        placeholder.markdown(
            f"""
            <div class="bubble-row">
                <div class="bubble assistant">
                    <div class="bubble-eyebrow">Urbane</div>
                    {answer}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state["messages"].append({"role": "assistant", "content": answer})
