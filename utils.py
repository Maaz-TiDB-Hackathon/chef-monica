import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from datetime import date
import pytz
from streamlit_js_eval import streamlit_js_eval

# Get the user's timezone using JavaScript
def get_user_timezone():
    timezone = streamlit_js_eval(
        js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone",
        key="timezone"
    )
    if not timezone:
        timezone = 'America/Los_Angeles'  # Default timezone
    return pytz.timezone(timezone)

def get_time_in_user_timezone(dt):
    """
    Converts a given datetime to the user's timezone.
    Args:
        dt (datetime): The datetime object to be converted.
    Returns:
        datetime: The converted datetime object in the user's timezone.
    """
    cest_timezone = pytz.timezone('Europe/Berlin')
    cest_datetime = cest_timezone.localize(dt)
    return cest_datetime.astimezone(get_user_timezone())

def get_user_profile():
    current_user = st.session_state.current_user
    user_profile = {"name": current_user.full_name, "email": current_user.email}
    return user_profile

def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})
    # Write to UI
    with st.chat_message(role):
        st.markdown(content)

def get_session_id():
    return get_script_run_ctx().session_id