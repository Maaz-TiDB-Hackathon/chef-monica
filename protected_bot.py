import streamlit as st
import crud
from models import ChatCreate, UserCreate
import re
from PIL import Image
from utils import get_time_in_user_timezone, get_user_profile, write_message
from langgraph_agent import generate_response, clear_chat
import uuid
import textwrap
import json

im = Image.open("images/foodie.png")
st.set_page_config(
    page_title="Foodie",
    page_icon=im,
    layout="centered",
    initial_sidebar_state="expanded"
)

def get_bot_intro_message():
    return {"role": "assistant", "content": "I am Chef Monica, a food expert here to provide you with detailed information about recipes and nutritional information from the USDA database. How can I assist you today?"}

def write_bot_intro_message():
    st.session_state.messages = [
            get_bot_intro_message()
        ]

def create_new_chat_if_required():
    if 'chat_id' in st.session_state and st.session_state.chat_id is not None:
        return False
    st.session_state.chat_id =  str(uuid.uuid1())
    crud.create_new_chat(ChatCreate(id = st.session_state.chat_id, user_id = st.session_state.current_user.id, 
                                    messages=[st.session_state.messages[0]]))
    return True

def append_message_to_chat():
    crud.append_message_to_chat(st.session_state.chat_id, st.session_state.messages[-1])

@st.dialog("Registration Attempt")
def registration_attempt(email, full_name, password):
    with st.spinner('Registering...'):
        if validate_email(email) is None or validate_password(password) is None or validate_name(full_name) is None:
            st.error("Invalid Data")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = register_user(email, full_name, password)
            if success:
                st.success(message)
            else:
                st.error(message)

@st.dialog("Login Attempt")
def login_attempt(email,password):
    with st.spinner('Logging in...'):
        if validate_email(email) is None or validate_password(password) is None:
            st.error("Invalid Data")
        else:
            success, message, user = login_user(email, password)
            if success: 
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.success(message)
                st.rerun()
            else:
                st.error(message)

@st.dialog("Chat Preview")
def chat_preview_dialog(chat):
    created_at = get_time_in_user_timezone(chat.created_at)
    st.caption(created_at.strftime("%Y-%m-%d %H:%M"))
    for message in chat.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with st.sidebar:
    st.image("images/foodie.png", use_container_width=True)
    if 'logged_in' in st.session_state and st.session_state.logged_in==True:
        col1, col2 = st.columns(2)
        with col1:
            logout = st.button("Logout", type="primary")
        with col2:
            new_chat = st.button("New ✍️", type="primary")
        if logout:
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.messages = []
            if 'chat_id' in st.session_state:
                clear_chat()
                st.session_state.chat_id = None
            st.rerun()

        if new_chat:
            st.session_state.messages = []
            clear_chat()
            st.session_state.chat_id = None
            write_bot_intro_message()
            st.rerun()
        chats = crud.get_all_chats_for_user(st.session_state.current_user.id)
        st.caption(f"History: {len(chats)} {'chat' if len(chats) == 1 else 'chats'}")
        for chat in chats:
            shortened_text = textwrap.shorten(chat.messages[1]["content"], width=40, placeholder="...")
            if st.button(shortened_text, key=chat.id, type="secondary"):
                chat_preview_dialog(chat)

def validate_name(name):
    name_pattern = r"^[A-Za-z\s-]{2,}$"
    return re.fullmatch(name_pattern, name)

def validate_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(email_regex, email)

def validate_password(password):
    password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&.*()]).{8,12}$"
    return re.fullmatch(password_regex, password)

def register_user(email, full_name, password):
    if crud.get_user_by_email(email) is not None:
        return False, "Email already exists."
    crud.create_user(UserCreate(email=email, full_name=full_name, password=password))
    return True, "Registration successful! Please login."

def login_user(email, password):
    user = crud.get_user_by_email(email)
    if user is None:
        return False, "Invalid username or password.", ""
    if crud.check_password(password, user.hashed_password):
        user.hashed_password=None
        return True, "Login successful.", user
    else:
        return False, "Invalid username or password.", ""

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.logged_in:
    st.title("Login / Register")
    choice = st.radio(
        "Choose an option:",
        ["Login", "Register"],
        key='login_or_register'
    )
    if choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            if email:
                if validate_email(email):
                    st.success("Email format is valid!")
                else:
                    st.error("Invalid email format. Please enter a valid email address.")
            password = st.text_input("Password", type="password")
            if password:
                if validate_password(password):
                    st.success("Password meets strength requirements!")
                else:
                    st.error("Password does not meet requirements. Ensure it has 8-12 characters, including uppercase, lowercase, numbers, and special characters.")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                login_attempt(email, password)

    elif choice == "Register":
        with st.form("register_form"):
            email = st.text_input("Email")
            if email:
                if validate_email(email):
                    st.success("Email format is valid!")
                else:
                    st.error("Invalid email format. Please enter a valid email address.")
            full_name = st.text_input("Full Name")
            if full_name:
                if validate_name(full_name):
                    st.success("Name is valid!")
                else:
                    st.error("Invalid name: Only letters, spaces, and hyphens allowed, and must be at least 2 characters long.")
            password = st.text_input("Password", type="password")
            if password:
                if validate_password(password):
                    st.success("Password meets strength requirements!")
                else:
                    st.error("Password does not meet requirements. Ensure it has 8-12 characters, including uppercase, lowercase, numbers, and special characters.")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")

            if register_button:
                registration_attempt(email, full_name, password)
  
else:
    st.title('Foodie')
    if "messages" not in st.session_state or st.session_state.messages==[]:
        write_bot_intro_message()

    def handle_submit(message):
        """
        Submit handler:
        """

        with st.spinner('Thinking...'):
            # Call the agent
            append_message_to_chat()
            response = generate_response(message)
            write_message('assistant', response)
            append_message_to_chat()

    for message in st.session_state.messages:
        write_message(message['role'], message['content'], save=False)

    if question := st.chat_input("Ask something..."):
        write_message('user', question)
        if create_new_chat_if_required():
            user_profile = get_user_profile()
            question += '\n' + str(user_profile)
            print(user_profile)
        handle_submit(question)