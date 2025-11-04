import streamlit as st
import sys
import os

# Adicionar o diretório raiz ao path para importar os serviços
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro - Kayke",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .alert-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.title("💰 Sistema Financeiro Kayke")
    st.sidebar.markdown("---")
    
    st.markdown('<h1 class="main-header">💰 Dashboard Financeiro</h1>', unsafe_allow_html=True)
    
    st.info("""
    🎯 **Bem-vindo ao seu Sistema Financeiro Pessoal!**
    
    Use o menu lateral para navegar entre as páginas:
    - **📊 Dashboard**: Visão geral das suas finanças
    - **📅 Controle Diário**: Acompanhamento dia a dia  
    - **💸 Transações**: Ver e editar todas as transações
    - **🎯 Método Breno**: Análise do método de economia
    - **📈 Relatórios**: Relatórios detalhados e tendências
    """)
    
    # Métricas rápidas na página inicial
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🚀 Status", "Sistema Ativo", "100%")
    
    with col2:
        st.metric("💡 Dica do Dia", "Monitore seus gastos", "📱")
    
    with col3:
        st.metric("🎯 Objetivo", "Economia 25%", "✅")

if __name__ == "__main__":
    main()