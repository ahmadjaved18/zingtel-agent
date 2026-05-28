import builtins
import html
import importlib
import os
import sys
import uuid
import traceback

import streamlit as st


st.set_page_config(
    page_title="ZingTel Support — Zara AI Agent",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

FALLBACK_MESSAGE = (
    "Zara is not available right now because the API limit has been reached. "
    "Please try again later."
)


@st.cache_resource(show_spinner=False)
def load_agent_module(api_key_override: str | None = None):
    original_input = builtins.input
    original_api_key = os.environ.get("GEMINI_API_KEY")
    if api_key_override:
        os.environ["GEMINI_API_KEY"] = api_key_override
    builtins.input = lambda *args, **kwargs: "quit"
    try:
        if "app" in sys.modules:
            return importlib.reload(sys.modules["app"])
        return importlib.import_module("app")
    finally:
        builtins.input = original_input
        if original_api_key is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = original_api_key


QUICK_PROMPTS = [
    "How do I activate my ZingTel SIM?",
    "Tell me about the premium package.",
    "How do I escalate a complaint?",
]


if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"streamlit_{uuid.uuid4().hex}"

if "api_key_override" not in st.session_state:
    st.session_state.api_key_override = ""

with st.sidebar:
    st.sidebar.title("ZingTel Support")
    st.sidebar.markdown(
        """
**Zara** can help you with:
- 📦 Package information
- 💰 Billing and refunds
- 🔧 Technical support
- 📡 Network status
"""
    )

    st.sidebar.success("🟢 Zara is online")
    st.session_state.api_key_override = st.sidebar.text_input(
        "API key (optional for local testing)",
        value=st.session_state.api_key_override,
        type="password",
        help="Use this only for local testing. For Streamlit Cloud, keep the key in Secrets.",
    )

app_module = load_agent_module(st.session_state.api_key_override or None)


def get_zara_response(user_input: str) -> str:
    try:
        return app_module.chat(user_input)
    except Exception as exc:
        tb = traceback.format_exc()
        try:
            with open('zingtel_error.log', 'a', encoding='utf-8') as f:
                f.write('\n---\n')
                f.write(tb)
        except Exception:
            pass
        st.session_state['last_error'] = tb
        error_text = str(exc).lower()
        quota_signals = (
            "groq",
            "quota",
            "rate limit",
            "resource_exhausted",
            "429",
            "too many requests",
            "exhausted",
            "insufficient_quota",
            "authentication",
            "unauthorized",
        )
        if any(signal in error_text for signal in quota_signals):
            return FALLBACK_MESSAGE

        return FALLBACK_MESSAGE


st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(16, 130, 255, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(7, 221, 163, 0.12), transparent 24%),
                linear-gradient(180deg, #06101d 0%, #081625 100%);
            color: #eef4fb;
        }

        [data-testid="stHeader"],
        #MainMenu,
        footer {
            visibility: hidden !important;
            display: none !important;
        }

        header[data-testid="stHeader"] {
            background: rgba(6, 16, 29, 0.92) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(153, 188, 255, 0.10);
        }

        div[data-testid="stToolbar"] {
            background: transparent !important;
        }

        header[data-testid="stHeader"] svg,
        header[data-testid="stHeader"] button,
        div[data-testid="stToolbar"] svg,
        div[data-testid="stToolbar"] button {
            color: #eef4fb !important;
            fill: #eef4fb !important;
            stroke: #eef4fb !important;
        }

        header[data-testid="stHeader"] svg *,
        div[data-testid="stToolbar"] svg * {
            fill: #eef4fb !important;
            stroke: #eef4fb !important;
        }

        header[data-testid="stHeader"] button:hover,
        div[data-testid="stToolbar"] button:hover {
            background: rgba(25, 130, 255, 0.12) !important;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.1rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #081221 0%, #06101d 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f5f8fc;
        }

        .brand-card {
            padding: 1.25rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.10);
            margin-bottom: 1rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }

        .logo-placeholder {
            width: 72px;
            height: 72px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.9rem;
            background: linear-gradient(135deg, #0b69ff 0%, #0f9dff 100%);
            color: white;
            margin-bottom: 0.75rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(10, 165, 90, 0.16);
            border: 1px solid rgba(10, 165, 90, 0.35);
            color: #d8f9e4;
            font-size: 0.92rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #17d66b;
            box-shadow: 0 0 0 4px rgba(23, 214, 107, 0.16);
        }

        .chat-shell {
            max-width: 980px;
            margin: 0 auto;
            padding-top: 0.25rem;
            padding-bottom: 0.75rem;
        }

        .hero-panel {
            max-width: 980px;
            margin: 1rem auto 1rem auto;
            padding: 1.2rem 1.3rem;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(14px);
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(25, 130, 255, 0.16);
            border: 1px solid rgba(25, 130, 255, 0.24);
            color: #d9ebff;
            font-size: 0.82rem;
            margin-bottom: 0.75rem;
        }

        .transcript-card {
            max-width: 980px;
            margin: 0 auto 1rem auto;
            padding: 1rem;
            border-radius: 26px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.20);
            backdrop-filter: blur(14px);
        }

        .transcript-scroll {
            max-height: calc(100vh - 320px);
            overflow-y: auto;
            padding-right: 0.25rem;
            scrollbar-width: thin;
            scrollbar-color: rgba(153, 188, 255, 0.45) transparent;
        }

        .transcript-scroll::-webkit-scrollbar {
            width: 10px;
        }

        .transcript-scroll::-webkit-scrollbar-thumb {
            background: rgba(153, 188, 255, 0.35);
            border-radius: 999px;
        }

        .transcript-scroll::-webkit-scrollbar-track {
            background: transparent;
        }

        .chat-message {
            padding: 0.9rem 1rem;
            border-radius: 18px;
            margin: 0.4rem 0;
            line-height: 1.5;
            max-width: 82%;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
            word-wrap: break-word;
            white-space: normal;
        }

        .chat-row {
            display: flex;
            width: 100%;
            margin: 0.25rem 0;
        }

        .chat-row.user {
            justify-content: flex-end;
        }

        .chat-row.assistant {
            justify-content: flex-start;
        }

        .chat-message.user {
            background: linear-gradient(135deg, #0b69ff 0%, #1982ff 100%);
            color: white;
            border-bottom-right-radius: 6px;
        }

        .chat-message.assistant {
            background: rgba(12, 22, 37, 0.95);
            color: #eaf2fb;
            border-bottom-left-radius: 6px;
            border: 1px solid rgba(153, 188, 255, 0.14);
        }

        .chat-meta {
            font-size: 0.82rem;
            opacity: 0.8;
            margin-bottom: 0.25rem;
        }

        .hero-title {
            font-size: clamp(2rem, 3.5vw, 3rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #ffffff;
            margin: 0;
        }

        .hero-subtitle {
            color: rgba(255, 255, 255, 0.84);
            margin-top: 0.35rem;
            font-size: 1rem;
            max-width: 70ch;
        }

        .chat-actions {
            max-width: 980px;
            margin: 0 auto 0.75rem auto;
            display: flex;
            justify-content: flex-end;
        }

        .chat-actions .stButton button {
            border-radius: 14px;
            border: 1px solid rgba(153, 188, 255, 0.18);
            background: rgba(255, 255, 255, 0.05);
            color: #eef4fb;
            padding: 0.45rem 0.9rem;
        }

        .chat-actions .stButton button:hover {
            background: rgba(25, 130, 255, 0.14);
            border-color: rgba(25, 130, 255, 0.35);
        }

        .stSpinner > div {
            color: #0b69ff;
        }

        section[data-testid="stSidebar"] .stButton button {
            border-radius: 14px;
            border: 1px solid rgba(153, 188, 255, 0.18);
            background: rgba(255, 255, 255, 0.05);
            color: #eef4fb;
            padding: 0.55rem 0.75rem;
        }

        section[data-testid="stSidebar"] .stButton button:hover {
            background: rgba(25, 130, 255, 0.14);
            border-color: rgba(25, 130, 255, 0.35);
        }

        @media (max-width: 768px) {
            .chat-message {
                max-width: 92%;
            }

            .hero-panel {
                margin-top: 0.75rem;
            }

            .transcript-scroll {
                max-height: calc(100vh - 360px);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.sidebar.title("ZingTel Support")
    st.sidebar.markdown(
        """
**Zara** can help you with:
- 📦 Package information
- 💰 Billing and refunds
- 🔧 Technical support
- 📡 Network status
"""
    )

    st.sidebar.success("🟢 Zara is online")

    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.markdown('<div class="logo-placeholder">📡</div>', unsafe_allow_html=True)
    st.markdown("### ZingTel")
    st.caption("Zara AI customer support")
    st.markdown(
        '<div class="status-pill"><span class="status-dot"></span> Ready</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"streamlit_{uuid.uuid4().hex}"
        st.session_state.composer_text = ""
        app_module.config["configurable"]["thread_id"] = st.session_state.thread_id
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.88rem; line-height:1.45; opacity:0.92;">
            <div><strong>Agent:</strong> Zara</div>
            <div><strong>Mode:</strong> RAG + Memory + Web Search</div>
            <div><strong>Brand:</strong> ZingTel Support</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Debug: show last exception if present
    if st.session_state.get('last_error'):
        with st.expander('Last error (debug)'):
            st.code(st.session_state.get('last_error'))
    st.sidebar.markdown("---")
    st.sidebar.caption("Built by Ahmad Javed")
    st.markdown("---")
    st.markdown("**Quick prompts**")
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    for quick_prompt in QUICK_PROMPTS:
        if st.button(quick_prompt, use_container_width=True, key=f"quick_{quick_prompt}"):
            st.session_state.messages.append({"role": "user", "content": quick_prompt})
            app_module.config["configurable"]["thread_id"] = st.session_state.thread_id
            status_slot = st.empty()
            status_slot.info("Zara is typing...")
            with st.spinner("Zara is thinking..."):
                response = get_zara_response(quick_prompt)
            status_slot.empty()
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    '<div class="hero-panel"><div class="hero-kicker">Telecom support assistant</div><h1 class="hero-title">ZingTel Support — Zara AI Agent</h1><p class="hero-subtitle">Ask about activation, billing, packages, complaints, or technical help. The conversation stays in this session and the transcript is designed to stay clean, readable, and scrollable.</p></div>',
    unsafe_allow_html=True,
)


app_module.config["configurable"]["thread_id"] = st.session_state.thread_id


_, top_actions_right = st.columns([8, 2])
with top_actions_right:
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"streamlit_{uuid.uuid4().hex}"
        app_module.config["configurable"]["thread_id"] = st.session_state.thread_id
        st.rerun()


chat_area = st.container()
with chat_area:
    transcript_parts = []
    for message in st.session_state.messages:
        role = message["role"]
        label = "Zara" if role == "assistant" else "You"
        row_class = "assistant" if role == "assistant" else "user"
        bubble_class = row_class
        rendered_content = html.escape(str(message["content"])).replace("\n", "<br>")
        transcript_parts.append(
            f'<div class="chat-row {row_class}"><div class="chat-message {bubble_class}"><div class="chat-meta">{label}</div>{rendered_content}</div></div>'
        )

    if transcript_parts:
        transcript_html = "".join(transcript_parts)
    else:
        transcript_html = (
            '<div class="chat-row assistant"><div class="chat-message assistant">'
            '<div class="chat-meta">Zara</div>Hello, I am Zara. How can I help you with ZingTel today?'
            '</div></div>'
        )

    st.markdown(
        f'<div class="transcript-card"><div class="transcript-scroll">{transcript_html}</div></div>',
        unsafe_allow_html=True,
    )

prompt = st.chat_input("Message Zara at ZingTel...")

if prompt:
    prompt = prompt.strip()
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        app_module.config["configurable"]["thread_id"] = st.session_state.thread_id
        status_slot = st.empty()
        status_slot.info("Zara is typing...")
        with st.spinner("Zara is thinking..."):
            response = get_zara_response(prompt)
        status_slot.empty()
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()