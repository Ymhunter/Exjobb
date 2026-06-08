import streamlit as st
import requests
import socket

def get_api_url():
    try:
        socket.gethostbyname("api")
        return "http://api:8000"
    except socket.gaierror:
        return "http://localhost:8000"

API_URL = get_api_url()

st.set_page_config(page_title="AI Waiter Chat", page_icon="🤖")
st.title("🤖 AI Waiter")

# Sidebar for PDF Menu Download
with st.sidebar:
    st.markdown("### 📋 Restaurant Menus")
    
    try:
        # Fetch the list of PDF menus from the FastAPI backend
        res = requests.get(f"{API_URL}/menu/pdf")
        if res.status_code == 200:
            pdf_files = res.json().get("files", [])
            if not pdf_files:
                st.info("No PDF menus available.")
            else:
                for filename in pdf_files:
                    clean_name = filename.replace(".pdf", "").replace("_", " ").title()
                    with st.expander(f"📄 {clean_name}"):
                        # Fetch specific PDF bytes
                        file_res = requests.get(f"{API_URL}/menu/pdf/{filename}")
                        if file_res.status_code == 200:
                            st.download_button(
                                label="Download PDF",
                                data=file_res.content,
                                file_name=filename,
                                mime="application/pdf",
                                key=f"dl_{filename}",
                                use_container_width=True
                            )
                            st.markdown(f"[📖 Open in New Tab](http://localhost:8000/menu/pdf/{filename})")
                        else:
                            st.error("Error loading file.")
        else:
            st.info("No PDF menus available.")
    except Exception as e:
        st.warning("Could not load PDF menus from backend.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! I am your AI Waiter. What can I get for you today? You can place an order or ask for recommendations."}
    ]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Place an order, ask a question, or get a recommendation..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from FastAPI backend
    try:
        res = requests.post(f"{API_URL}/chat", json={"text": prompt})
        if res.status_code == 200:
            bot_reply = res.json().get("response", "Sorry, I didn't understand.")
        else:
            bot_reply = f"System Error: {res.status_code}"
    except Exception as e:
        bot_reply = "Could not connect to the kitchen (backend server is down)."

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
