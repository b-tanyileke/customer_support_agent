"""
Streamlit chat UI for the Enterprise AI Support Agent.
"""

from pathlib import Path
import sys
import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import API_URL


EXAMPLE_QUESTIONS = [
    "What happens if my Auto-Pay fails?",
    "Can I unlock my phone after 45 days?",
    "My phone says No Service. What should I check first?",
    "Which plan includes Netflix and a lot of hotspot data?",
]


st.set_page_config(
    page_title="WEE Mobile Support Assistant",
    page_icon="",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 980px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }
    .app-header {
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
    }
    .app-title {
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }
    .app-subtitle {
        color: #4b5563;
        font-size: 0.98rem;
        margin-top: 0.35rem;
    }
    .status-row {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.75rem;
    }
    .chip {
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 999px;
        color: #374151;
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.22rem 0.58rem;
    }
    .chip.ok {
        background: #ecfdf5;
        border-color: #a7f3d0;
        color: #047857;
    }
    .chip.warn {
        background: #fff7ed;
        border-color: #fed7aa;
        color: #c2410c;
    }
    .source-line {
        color: #4b5563;
        font-size: 0.9rem;
        margin: 0.1rem 0;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 8px;
        padding: 0.45rem 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_health() -> tuple[bool, str]:
    """Check the health of the API."""
    try:
        response = requests.get(f"{API_URL.rstrip('/')}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        model = data.get("model", "configured model")
        return True, f"Online - {model}"
    except requests.RequestException:
        return False, "API offline"


def ask_support_agent(question: str) -> dict:
    """Send a question to the support agent API and return the response."""
    response = requests.post(
        f"{API_URL.rstrip('/')}/query",
        json={"question": question},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def add_user_message(content: str) -> None:
    """Add a user message to the session state."""
    st.session_state.messages.append({"role": "user", "content": content})


def add_assistant_message(data: dict) -> None:
    """Add an assistant message to the session state."""
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": data.get("response", ""),
            "intent": data.get("intent", "unknown"),
            "sources": data.get("sources", []),
            "escalated": data.get("escalated", False),
        }
    )


def render_assistant_metadata(message: dict) -> None:
    """Render the metadata for an assistant message."""
    intent = message.get("intent", "unknown")
    escalated = message.get("escalated", False)
    sources = message.get("sources", [])
    status_class = "warn" if escalated else "ok"
    status_text = "Escalated" if escalated else "Answered"

    st.markdown(
        f"""
        <div class="status-row">
            <span class="chip">Intent: {intent}</span>
            <span class="chip {status_class}">{status_text}</span>
            <span class="chip">{len(sources)} source(s)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if sources:
        with st.expander("Sources"):
            for source in sources:
                score = source.get("score")
                score_text = f" - similarity {score:.2f}" if isinstance(score, float) else ""
                st.markdown(
                    f"<p class=\"source-line\">{source.get('source', 'unknown')}{score_text}</p>",
                    unsafe_allow_html=True,
                )


def render_message(message: dict) -> None:
    """Render a chat message in the Streamlit UI."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_assistant_metadata(message)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I am the WEE Mobile support assistant. Ask me about billing, "
                "device troubleshooting, service terms, or product plans."
            ),
            "intent": "Greeting",
            "sources": [],
            "escalated": False,
        }
    ]

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

api_online, api_status = get_api_health()

with st.sidebar:
    st.header("Support Console")
    st.caption(f"API: {API_URL.rstrip('/')}")
    st.markdown(
        f"<span class=\"chip {'ok' if api_online else 'warn'}\">{api_status}</span>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Try an Example")
    for index, question in enumerate(EXAMPLE_QUESTIONS):
        if st.button(question, key=f"example_{index}", use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

st.markdown(
    """
    <div class="app-header">
        <h1 class="app-title">WEE Mobile Support Assistant</h1>
        <div class="app-subtitle">
            Online support for billing, device troubleshooting, service terms, and plan questions.
        </div>
        <div class="status-row">
            <span class="chip ok">Knowledge base enabled</span>
            <span class="chip">RAG support</span>
            <span class="chip">Human escalation aware</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

for chat_message in st.session_state.messages:
    render_message(chat_message)

prompt = st.chat_input("Ask a support question...")
question_to_send = st.session_state.pending_question or prompt
st.session_state.pending_question = None

if question_to_send:
    add_user_message(question_to_send)
    with st.chat_message("user"):
        st.markdown(question_to_send)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base and preparing an answer..."):
            try:
                answer = ask_support_agent(question_to_send)
            except requests.RequestException as exc:
                answer = {
                    "response": f"API request failed: {exc}",
                    "intent": "Error",
                    "sources": [],
                    "escalated": True,
                }

        st.markdown(answer["response"])
        assistant_message = {
            "role": "assistant",
            "content": answer["response"],
            "intent": answer.get("intent", "unknown"),
            "sources": answer.get("sources", []),
            "escalated": answer.get("escalated", False),
        }
        render_assistant_metadata(assistant_message)

    add_assistant_message(answer)
