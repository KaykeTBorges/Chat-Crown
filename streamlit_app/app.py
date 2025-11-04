import streamlit as st
import sys
import os
from datetime import datetime
# Adicionar o diretório raiz ao path para importar os serviços
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.database import db_manager



# Configuração da página
st.set_page_config(
    page_title="Sistema Financeiro - Chat Crown",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado melhorado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .quick-action-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .quick-action-card:hover {
        border-color: #1f77b4;
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Função para buscar user_id a partir do token
def get_user_id_from_token(token: str):
    from models.magic_link import MagicLink
    with db_manager.get_session() as session:
        magic_link = session.query(MagicLink).filter_by(token=token).first()
        if magic_link and magic_link.expires_at > datetime.utcnow():
            return magic_link.user_id
    return None

# Inicializa user_id na sessão
if "user_id" not in st.session_state:
    # Usando a nova API st.query_params
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


def main():
    st.sidebar.title("💰 Sistema Financeiro")
    st.sidebar.markdown("---")
    
    # Menu de navegação melhorado
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
    
    # Redirecionamento baseado na seleção
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
    else:
        # Página inicial padrão
        st.markdown('<h1 class="main-header">💰 Sistema Financeiro Pessoal</h1>', unsafe_allow_html=True)
        
        st.success("""
        🎉 **Bem-vindo ao seu Sistema Financeiro Inteligente!**
        
        Use o menu lateral para navegar ou comece por uma das ações rápidas abaixo:
        """)
        
        # Ações rápidas na página inicial
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Ver Dashboard", use_container_width=True):
                st.switch_page("pages/1_📊_Dashboard.py")
        
        with col2:
            if st.button("💸 Gerenciar Transações", use_container_width=True):
                st.switch_page("pages/3_💸_Transações.py")
        
        with col3:
            if st.button("🎯 Acompanhar Metas", use_container_width=True):
                st.switch_page("pages/6_🎯_Metas.py")
        
        with col4:
            if st.button("⚡ Ver Alertas", use_container_width=True):
                st.switch_page("pages/7_⚡_Alertas.py")
        
        # Status rápido do sistema
        st.markdown("---")
        st.subheader("📈 Status do Sistema")
        
        try:
            from services.database import db_manager
            
            with db_manager.get_session() as session:
                from models.transaction import Transaction
                from models.goal import FinancialGoal
                
                total_transactions = session.query(Transaction).filter(Transaction.user_id == 1).count()
                total_goals = session.query(FinancialGoal).filter(FinancialGoal.user_id == 1).count()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Transações", total_transactions)
            
            with col2:
                st.metric("Metas Ativas", total_goals)
            
            with col3:
                st.metric("Status", "✅ Ativo")
                
        except Exception as e:
            st.error(f"Erro ao carregar status: {e}")

if __name__ == "__main__":
    main()