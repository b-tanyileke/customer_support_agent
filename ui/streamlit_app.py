"""
Streamlit Interface for AI support agent.
"""

# Import libraries
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/query"

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
        response = requests.post(
            API_URL, 
            json={"question": user_input},
            timeout=60
            ).json()

    st.markdown("## Response")
    st.write(response["response"])
    