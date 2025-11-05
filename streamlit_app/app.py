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

if "user_id" not in st.session_state:
    st.session_state.user_id = None

def lookup_token(token: str):
    """Retorna user_id se token válido, senão None. Também retorna debug info."""
    if not token:
        return None, "token vazio"

    with db_manager.get_session() as session:
        # Debug: listar matching tokens exatos (mostra None se não achar)
        ml = session.query(MagicLink).filter(MagicLink.token == token).first()
        # opcional: listar todos os tokens recentes (apenas debug)
        recent = session.query(MagicLink).order_by(MagicLink.created_at.desc()).limit(10).all()
        debug = {
            "found": bool(ml),
            "found_token": ml.token if ml else None,
            "found_user_id": ml.user_id if ml else None,
            "found_expires_at": ml.expires_at if ml else None,
            "recent_tokens": [(r.token, r.user_id, r.expires_at) for r in recent]
        }
        if ml:
            # verificação de expiração - comparando UTC
            now = datetime.utcnow()
            if ml.expires_at and ml.expires_at > now:
                return ml.user_id, debug
            else:
                return None, debug
        else:
            return None, debug

# ------------------ PEGAR TOKEN DA URL CORRETAMENTE ------------------
# st.query_params sempre retorna listas como valores; pegue [0]
token_param = None
try:
    token_param = st.query_params.get("token", [None])[0]
except Exception:
    # fallback robusto
    params = dict(st.query_params)
    token_param = params.get("token")
    if isinstance(token_param, list):
        token_param = token_param[0]

st.write("🔍 Token recebido na URL (raw):", token_param)

# Tenta validar token vindo da URL
if token_param:
    user_id, debug_info = lookup_token(token_param)
    st.write("🔎 Debug lookup:", debug_info)
    if user_id:
        st.session_state.user_id = user_id
        st.success(f"✅ Token válido — user_id setado ({user_id})")
    else:
        st.warning("⚠️ Token da URL inválido/expirado ou não encontrado.")
        # mostra opção manual
        pasted = st.text_input("Cole aqui o token (fallback manual):", value="")
        if st.button("Validar token colado"):
            manual_user_id, manual_debug = lookup_token(pasted.strip())
            st.write("🔎 Debug manual:", manual_debug)
            if manual_user_id:
                st.session_state.user_id = manual_user_id
                st.success(f"✅ Token válido — user_id setado ({manual_user_id})")
                # opcional: redirect para limpar query params usando st.experimental_set_query_params
                st.experimental_set_query_params()
                st.experimental_rerun()
            else:
                st.error("❌ Token colado inválido ou expirado.")
else:
    st.info("Navegando sem token na URL. Cole o token abaixo (recebido via bot).")
    pasted = st.text_input("Cole aqui o token:", value="")
    if st.button("Validar token colado"):
        manual_user_id, manual_debug = lookup_token(pasted.strip())
        st.write("🔎 Debug manual:", manual_debug)
        if manual_user_id:
            st.session_state.user_id = manual_user_id
            st.success(f"✅ Token válido — user_id setado ({manual_user_id})")
            st.experimental_set_query_params()
            st.experimental_rerun()
        else:
            st.error("❌ Token inválido ou expirado.")

# DEBUG ADVANCED (apenas se você quiser listar tokens no DB — remova em prod)
if st.checkbox("🛠️ Mostrar tokens recentes (DEBUG)", value=False):
    with db_manager.get_session() as session:
        recent = session.query(MagicLink).order_by(MagicLink.created_at.desc()).limit(50).all()
        st.write("Tokens recentes (token, user_id, expires_at):")
        st.write([(r.token, r.user_id, r.expires_at) for r in recent])

# Final: se user_id foi setado, segue o app; se não, paramos.
if st.session_state.user_id is None:
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
