# streamlit_app/app.py
import streamlit as st
import requests
from services.users_service import users_service
from config.config import config

st.set_page_config(page_title="Sistema Financeiro", page_icon="💰", layout="wide")

# --- LÓGICA DE AUTENTICAÇÃO ---

# Se o usuário já está logado, mostra o app
if 'telegram_id' in st.session_state and st.session_state['telegram_id']:
    # Carrega os dados do usuário se ainda não foram carregados
    if 'user' not in st.session_state:
        st.session_state['user'] = users_service.get_user_by_telegram_id(st.session_state['telegram_id'])

    # --- BLOCO DA INTERFACE DO USUÁRIO LOGADO ---
    from utils import display_user_info
    display_user_info()

    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navegação Principal:",
        [
            "🚀 Início Rápido",
            "📊 Dashboard",
            "📅 Controle Diário",
            "💸 Transações",
            "🎯 Metas e Orçamentos",
            "📈 Relatórios"
        ]
    )
    page_mapping = {
        "🚀 Início Rápido": "pages/0_🚀_Início_Rápido.py",
        "📊 Dashboard": "pages/1_📊_Dashboard.py",
        "📅 Controle Diário": "pages/4_📅_Controle_Diário.py",
        "💸 Transações": "pages/2_💸_Transações.py",
        "🎯 Metas e Orçamentos": "pages/3_🎯_Metas_e_Orçamentos.py",
        "📈 Relatórios": "pages/5_📈_Relatórios.py"
    }
    if page in page_mapping:
        st.switch_page(page_mapping[page])

# Se não está logado, mostra a página de login
else:
    st.markdown('<h1 class="main-header">👑 Chat Crown - Login</h1>', unsafe_allow_html=True)
    
    st.info("Para acessar seu painel, digite `/login` no bot do Telegram para receber seu código de acesso.")
    
    with st.form("login_form"):
        code = st.text_input("Digite seu código de 6 dígitos:", max_chars=6, placeholder="123456")
        submitted = st.form_submit_button("Acessar")

        if submitted:
            if not code or len(code) != 6 or not code.isdigit():
                st.error("Por favor, digite um código válido de 6 dígitos.")
            else:
                with st.spinner("Validando código..."):
                    try:
                        response = requests.post(f"{config.API_URL}/auth/validate_code", data={"code": code})
                        if response.status_code == 200:
                            data = response.json()
                            telegram_id = data.get("telegram_id")
                            
                            # Cria a sessão do usuário
                            st.session_state['telegram_id'] = telegram_id
                            st.session_state['user'] = users_service.get_user_by_telegram_id(telegram_id)
                            
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Código inválido ou expirado. Verifique o código ou gere um novo no bot.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Não foi possível conectar ao serviço de autenticação. Erro: {e}")