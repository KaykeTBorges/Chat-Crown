# streamlit_app/app.py
import streamlit as st
from config import config
from services.auth_service import AuthService
from services.users_service import UsersService

st.set_page_config(
    page_title="Sistema Financeiro - Chat Crown",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- LOGIN TELEGRAM OAUTH --------------------
def require_login():
    """Valida login pelo Telegram OAuth e mantém na sessão."""
    if "user_id" in st.session_state:
        return  # já logado

    # Coleta valores da URL vindos do Telegram
    raw_params = st.query_params
    data = {k: v[0] for k, v in raw_params.items()} if raw_params else {}

    # Se o Telegram enviou id + hash → tentamos validar
    if "id" in data and "hash" in data:
        if AuthService.verify_telegram_auth(data.copy()):
            st.session_state.user_id = int(data["id"])
            st.experimental_set_query_params()  # remove info sensível da URL
            st.experimental_rerun()
        else:
            st.error("❌ Não foi possível autenticar. Tente novamente pelo /painel no bot.")
            st.stop()

    # Nenhum login → Mostra botão de login
    login_url = (
        "https://oauth.telegram.org/auth?"
        f"bot_id={config.TELEGRAM_BOT_USERNAME}&"
        f"origin={config.STREAMLIT_URL}&"
        f"return_to={config.STREAMLIT_URL}"
    )

    st.markdown("## 🔐 Login Necessário")
    st.markdown(f"""
    <a href="{login_url}" style="
        font-size:20px;
        padding:12px 18px;
        background:#4b9be5;
        color:white;
        border-radius:8px;
        text-decoration:none;">
        👉 Entrar com Telegram
    </a>
    """, unsafe_allow_html=True)
    st.stop()


# -------------------- EXECUTA LOGIN --------------------
require_login()
user = UsersService.get_user_by_id(st.session_state.user_id)


# -------------------- Cabeçalho --------------------
st.markdown('<h1 class="main-header">💰 Sistema Financeiro Pessoal</h1>', unsafe_allow_html=True)

# -------------------- Menu Lateral --------------------
st.sidebar.title(f"👤 {user.first_name or 'Usuário'}")
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
