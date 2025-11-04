# pages/0_🚀_Início_Rápido.py
import streamlit as st
from services.transactions_service import transactions_service
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


st.set_page_config(page_title="Início Rápido", page_icon="🚀", layout="wide")

st.markdown('<h1 class="main-header">🚀 Início Rápido</h1>', unsafe_allow_html=True)

# ---------------------- Cards de ação rápida ----------------------
col1, col2, col3, col4 = st.columns(4)

cards = [
    {"emoji": "💸", "title": "Registrar Gastos", "desc": "Adicione transações rapidamente", "page": "pages/3_💸_Transações.py", "key": "quick_transactions", "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
    {"emoji": "🎯", "title": "Ver Metas", "desc": "Acompanhe seus objetivos", "page": "pages/6_🎯_Metas.py", "key": "quick_goals", "bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"},
    {"emoji": "📊", "title": "Dashboard", "desc": "Visão geral das finanças", "page": "pages/1_📊_Dashboard.py", "key": "quick_dashboard", "bg": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"},
    {"emoji": "⚡", "title": "Alertas", "desc": "Verifique notificações", "page": "pages/7_⚡_Alertas.py", "key": "quick_alerts", "bg": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"}
]

for i, card in enumerate(cards):
    with [col1, col2, col3, col4][i]:
        st.markdown(f"""
            <div style='background: {card['bg']}; 
                        color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h2>{card['emoji']}</h2>
                <h3>{card['title']}</h3>
                <p>{card['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"Acessar {card['title']}", key=card['key'], use_container_width=True):
            st.switch_page(card['page'])

# ---------------------- Últimas transações ----------------------
st.markdown("---")
st.subheader("📋 Últimas Transações")

try:
    recent_transactions = transactions_service.get_recent_transactions(
        user_id=st.session_state.user_id, limit=5
    )

    if recent_transactions:
        for t in recent_transactions:
            emoji = "💰" if t.type=="renda" else "💸" if "despesa" in t.type else "🚀"
            color = "#28a745" if t.type=="renda" else "#dc3545" if "despesa" in t.type else "#007bff"

            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                st.write(f"**{emoji} {t.description}**")
                st.caption(f"📅 {t.date.strftime('%d/%m/%Y')} | 📂 {t.category}")
            with col2:
                st.write(t.type.replace('_',' ').title())
            with col3:
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>R$ {t.amount:,.2f}</span>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("Nenhuma transação recente encontrada.")
except Exception as e:
    st.error(f"Erro ao carregar transações: {e}")

# ---------------------- Dicas rápidas ----------------------
st.markdown("---")
st.subheader("💡 Dicas Rápidas")

tips = [
    {"title": "📱 Use o Telegram", "text": "- Envie: \"almoço 25,50\"\n- Use: \"/resumo\" para ver o mês"},
    {"title": "🎯 Método Breno", "text": "- Economize 25% da renda\n- Controle gastos diários\n- Acompanhe no Controle Diário"},
    {"title": "🔍 Busca Avançada", "text": "- Use filtros nas transações\n- Exporte para CSV/JSON\n- Visualização compacta disponível"}
]

tip_cols = st.columns(3)
for i, tip in enumerate(tips):
    with tip_cols[i]:
        st.info(f"**{tip['title']}**\n{tip['text']}")
