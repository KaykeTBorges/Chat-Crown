# streamlit_app/utils.py
import streamlit as st
from datetime import datetime

def check_authentication():
    """
    Verifica se o usuário está autenticado.
    Se não estiver, exibe mensagem e para a execução da página.
    Retorna o telegram_id do usuário se autenticado.
    """
    if 'telegram_id' not in st.session_state or not st.session_state['telegram_id']:
        st.warning("🔐 Para acessar esta página, faça login no bot do Telegram.")
        st.stop()
    return st.session_state['telegram_id']

def month_year_filter(key_prefix=""):
    """
    Cria um filtro de mês e ano no Streamlit e retorna os valores selecionados.
    O `key_prefix` evita conflitos de `st.key` entre páginas.
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
            index=2, # Index para o ano atual
            key=f"{key_prefix}_year"
        )
    return month, year

def display_user_info():
    """Exibe as informações do usuário na sidebar."""
    user = st.session_state.get('user')
    if user:
        st.sidebar.title(f"👤 {user.first_name or 'Usuário'}")
        st.sidebar.caption(f"ID: {user.telegram_id}")
    else:
        st.sidebar.title("👤 Usuário")
        st.sidebar.caption("Não carregado")