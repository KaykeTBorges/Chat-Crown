import streamlit as st
from datetime import datetime


def check_authentication():
    """
    Ensure the current user is authenticated before rendering a page.

    If there is no `telegram_id` in the Streamlit session state, this function
    shows a warning and stops the page execution. When authentication is OK,
    it returns the `telegram_id` stored in the session.
    """
    if 'telegram_id' not in st.session_state or not st.session_state['telegram_id']:
        st.warning("🔐 Para acessar esta página, faça login no bot do Telegram.")
        st.stop()
    return st.session_state['telegram_id']

def month_year_filter(key_prefix=""):
    """
    Render a simple month/year selector and return the chosen values.

    The `key_prefix` parameter is used to avoid key collisions between
    different pages that might also create month/year selectors.
    """
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox(
            "Mês", 
            list(range(1, 13)), 
            index=datetime.now().month - 1, 
            key=f"{key_prefix}_month"
        )
    with col2:
        year = st.selectbox(
            "Ano",
            list(range(datetime.now().year - 2, datetime.now().year + 3)),
            index=2,  # Default index pointing at the current year.
            key=f"{key_prefix}_year",
        )
    return month, year

def display_user_info():
    """Show basic user information in the sidebar."""
    user = st.session_state.get('user')
    if user:
        st.sidebar.title(f"👤 {user.first_name or 'Usuário'}")
        st.sidebar.caption(f"ID: {user.telegram_id}")
    else:
        st.sidebar.title("👤 Usuário")
        st.sidebar.caption("Não carregado")