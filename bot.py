import streamlit as st
from utils import write_message
from agent import generate_response, clear_chat

# Page Config
st.set_page_config("Ebert", page_icon=":movie_camera:")
st.title("Chef Monica, your food expert")
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am Chef Monica, a food expert here to provide you with detailed information about recipes. How can I assist you today?"}
        ]

# Submit handler
def handle_submit(message):
    """
    Submit handler:
    """

    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if question := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)

# Add a button below the chat input
if st.button("Forget Chat"):
    st.session_state.messages = []
    clear_chat()
    st.rerun() # Rerun to clear the displayed chat

