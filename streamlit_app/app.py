# streamlit_app/app.py
import streamlit as st
import os
from datetime import datetime
from services.transactions_service import transactions_service
from services.database import db_manager
from models.magic_link import MagicLink
from services.users_service import UsersService
# -------------------- Inicialização --------------------
st.set_page_config(
    page_title="Sistema Financeiro - Chat Crown",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa user_id na sessão
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Função para buscar user_id a partir do token
def get_user_id_from_token(token: str):
    with db_manager.get_session() as session:
        magic_link = session.query(MagicLink).filter_by(token=token).first()
        if magic_link and magic_link.expires_at > datetime.utcnow():
            return magic_link.user_id
    return None

# --------------- Autenticação do usuário ----------------
if st.session_state.user_id is None:
    # 1️⃣ Pega token da URL
    token_list = st.query_params.get("token", [None])
    token = token_list[0] if token_list else None

    if token:
        user_id = get_user_id_from_token(token)
        if user_id:
            st.session_state.user_id = user_id
        else:
            st.error("❌ Link inválido ou expirado")
            st.stop()
    else:
        st.error("❌ Você precisa de um token para acessar esta página")
        st.stop()

user = UsersService.get_user_by_id(st.session_state.user_id)

# -------------------- Cabeçalho --------------------
st.markdown('<h1 class="main-header">💰 Sistema Financeiro Pessoal</h1>', unsafe_allow_html=True)

# -------------------- Menu Lateral --------------------
st.sidebar.title("💰 Sistema Financeiro")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegação Principal:",
    [
        "🚀 Início Rápido",
        "📊 Dashboard", 
        "📅 Controle Diário", 
        "💸 Transações", 
        "🎯 Método Breno", 
        "📈 Relatórios",
        "🎯 Metas",
        "⚡ Alertas"
    ]
)

page_mapping = {
    "🚀 Início Rápido": "pages/0_🚀_Início_Rápido.py",
    "📊 Dashboard": "pages/1_📊_Dashboard.py",
    "📅 Controle Diário": "pages/2_📅_Controle_Diário.py", 
    "💸 Transações": "pages/3_💸_Transações.py",
    "🎯 Método Breno": "pages/4_🎯_Método_Breno.py",
    "📈 Relatórios": "pages/5_📈_Relatórios.py",
    "🎯 Metas": "pages/6_🎯_Metas.py",
    "⚡ Alertas": "pages/7_⚡_Alertas.py"
}

if page in page_mapping:
    st.switch_page(page_mapping[page])

# -------------------- Página Inicial --------------------
else:
    st.success("""
    🎉 **Bem-vindo ao seu Sistema Financeiro Inteligente!**
    
    Use o menu lateral para navegar ou comece por uma das ações rápidas abaixo:
    """)

    # Ações rápidas
    col1, col2, col3, col4 = st.columns(4)
    actions = [
        ("📊 Ver Dashboard", "pages/1_📊_Dashboard.py", col1),
        ("💸 Gerenciar Transações", "pages/3_💸_Transações.py", col2),
        ("🎯 Acompanhar Metas", "pages/6_🎯_Metas.py", col3),
        ("⚡ Ver Alertas", "pages/7_⚡_Alertas.py", col4)
    ]

    for label, page_file, col in actions:
        with col:
            if st.button(label, use_container_width=True):
                st.switch_page(page_file)

    # Status rápido do sistema
    st.markdown("---")
    st.subheader("📈 Status do Sistema")

    try:
        user_id = st.session_state.user_id

        # Usa TransactionsService para pegar dados
        recent_transactions = transactions_service.get_recent_transactions(user_id=user_id, limit=5)
        total_transactions = len(recent_transactions)

        from models.goal import FinancialGoal
        with db_manager.get_session() as session:
            total_goals = session.query(FinancialGoal).filter(FinancialGoal.user_id == user_id).count()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Transações", total_transactions)
        col2.metric("Metas Ativas", total_goals)
        col3.metric("Status", "✅ Ativo")

    except Exception as e:
        st.error(f"Erro ao carregar status: {e}")
