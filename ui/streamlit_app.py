"""
Streamlit app for the Enterprise AI Support Agent.
This app allows users to ask questions related to billing, device issues, or service policies.
For complex issues, the agent may recommend escalation.
"""

import requests
import streamlit as st
from config import API_URL


st.set_page_config(page_title="Enterprise AI Support Agent")

st.title("Enterprise AI Support Agent")
st.write(
    "Ask questions related to billing, device issues, or service policies. "
    "For complex issues, the agent may recommend escalation."

)

# Chat input
user_input = st.text_input("Enter your question: ")

if st.button("Submit") and user_input:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL.rstrip('/')}/query",
                json={"question": user_input},
                timeout=90,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            st.error(f"API request failed: {exc}")
            st.stop()

    st.markdown("## Response")
    st.write(data["response"])

    st.caption(f"Intent: {data.get('intent', 'unknown')}")

    sources = data.get("sources", [])
    if sources:
        st.markdown("### Sources")
        for source in sources:
            score = source.get("score")
            score_text = f" - distance {score:.2f}" if isinstance(score, float) else ""
            st.write(f"- {source.get('source', 'unknown')}{score_text}")
