import streamlit as st
import pandas as pd
import requests

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("index.css")        

st.markdown(
    "<h1 class'app-title'> Movie Recommender Chatbot</h1>",
    unsafe_allow_html=True
)
st.set_page_config(page_title="Movie Recommender Bot", layout="centered")


st.markdown("Find any movie you want with this Rasa powered Chatbot.")

# Store conversation in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages
for msg in st.session_state["messages"]:
    role_class = "user-message" if msg["role"] == "user" else "bot-message"
    label_class = "user-label" if msg["role"] == "user" else "bot-label"
    speaker = "You" if msg["role"] == "user" else "Bot"
    st.markdown(
        f"<div class='{label_class}'>{speaker}</div>", 
        unsafe_allow_html=True)
    st.markdown(
        f"<div class='{role_class}'>{msg['content']}</div>", 
        unsafe_allow_html=True)

# User input box
if user_input := st.chat_input("Type your message..."):
    # Save user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Render with custom bubble immediately
    st.markdown("<div class='user-label'>You</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)


    # Send to Rasa
    response = requests.post(
        "http://localhost:5005/webhooks/rest/webhook",
        json={"sender": "streamlit_user", "message": user_input}
    )

    # Show bot response
    for r in response.json():
        print(r)
        bot_reply = r.get("text", "")
        if bot_reply:
            # Save bot message
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

            # Render bot label
            st.markdown("<div class='bot-label'>Bot</div>", unsafe_allow_html=True)

            # Detect fallback (don't tabulate)
            if "Sorry, I didn't get that" in bot_reply:
                st.markdown(f"<div class='bot-message'>{bot_reply}</div>", unsafe_allow_html=True)
                continue

            movies = []
            intro = ""
            if "\n" in bot_reply:
                intro = bot_reply.split("\n")[0]
                movies = [
                    line.strip("- ").strip()
                    for line in bot_reply.split("\n")
                    if line.strip().startswith("-")
                ]

            if movies and len(movies) > 1:
                st.markdown(f"<div class='bot-message'>{intro}</div>", unsafe_allow_html=True)
                df = pd.DataFrame({"{Recommended Movies}": movies})
                st.table(df)
            else:
                st.markdown(f"<div class='bot-message'>{bot_reply}</div>", unsafe_allow_html=True)



