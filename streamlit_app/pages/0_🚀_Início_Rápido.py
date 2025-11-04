import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Início Rápido", page_icon="🚀", layout="wide")

def main():
    st.markdown('<h1 class="main-header">🚀 Início Rápido</h1>', unsafe_allow_html=True)
    
    # Cards de ação rápida
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h2>💸</h2>
                <h3>Registrar Gastos</h3>
                <p>Adicione transações rapidamente</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Transações", key="quick_transactions", use_container_width=True):
                st.switch_page("pages/3_💸_Transações.py")
    
    with col2:
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h2>🎯</h2>
                <h3>Ver Metas</h3>
                <p>Acompanhe seus objetivos</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Metas", key="quick_goals", use_container_width=True):
                st.switch_page("pages/6_🎯_Metas.py")
    
    with col3:
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h2>📊</h2>
                <h3>Dashboard</h3>
                <p>Visão geral das finanças</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Dashboard", key="quick_dashboard", use_container_width=True):
                st.switch_page("pages/1_📊_Dashboard.py")
    
    with col4:
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h2>⚡</h2>
                <h3>Alertas</h3>
                <p>Verifique notificações</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Alertas", key="quick_alerts", use_container_width=True):
                st.switch_page("pages/7_⚡_Alertas.py")
    
    # Últimas transações (seção rápida)
    st.markdown("---")
    st.subheader("📋 Últimas Transações")
    
    try:
        from services.database import db_manager
        from datetime import datetime, timedelta
        
        # Buscar últimas 5 transações
        with db_manager.get_session() as session:
            from models.transaction import Transaction
            recent_transactions = session.query(Transaction).filter(
                Transaction.user_id == 1
            ).order_by(Transaction.date.desc()).limit(5).all()
        
        if recent_transactions:
            for transaction in recent_transactions:
                emoji = "💰" if transaction.type == 'renda' else "💸" if 'despesa' in transaction.type else "🚀"
                color = "#28a745" if transaction.type == 'renda' else "#dc3545" if 'despesa' in transaction.type else "#007bff"
                
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{emoji} {transaction.description}**")
                    st.caption(f"📅 {transaction.date.strftime('%d/%m/%Y')} | 📂 {transaction.category}")
                with col2:
                    st.write(transaction.type.replace('_', ' ').title())
                with col3:
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>R$ {transaction.amount:,.2f}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
        else:
            st.info("Nenhuma transação recente encontrada.")
            
    except Exception as e:
        st.error(f"Erro ao carregar transações: {e}")
    
    # Dicas rápidas
    st.markdown("---")
    st.subheader("💡 Dicas Rápidas")
    
    tip_col1, tip_col2, tip_col3 = st.columns(3)
    
    with tip_col1:
        st.info("""
        **📱 Use o Telegram**
        - Envie: "almoço 25,50"
        - Use: "/resumo" para ver o mês
        """)
    
    with tip_col2:
        st.info("""
        **🎯 Método Breno**
        - Economize 25% da renda
        - Controle gastos diários
        - Acompanhe no Controle Diário
        """)
    
    with tip_col3:
        st.info("""
        **🔍 Busca Avançada**
        - Use filtros nas transações
        - Exporte para CSV/JSON
        - Visualização compacta disponível
        """)

if __name__ == "__main__":
    main()