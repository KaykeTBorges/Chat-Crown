import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.transactions_service import transactions_service
from utils import check_authentication

st.set_page_config(page_title="Início Rápido", page_icon="🚀", layout="wide")

# Check if the user is logged in and get their Telegram ID.
telegram_id = check_authentication()

st.markdown('<h1 class="main-header">🚀 Início Rápido</h1>', unsafe_allow_html=True)

# --- Quick access navigation cards ---
st.subheader("⚡ Acesso Rápido")
col1, col2, col3, col4 = st.columns(4)
cards = [
    {"emoji": "💸", "title": "Transações", "page": "pages/3_💸_Transações.py"},
    {"emoji": "🎯", "title": "Metas e Orçamentos", "page": "pages/4_🎯_Metas_e_Orçamentos.py"},
    {"emoji": "📊", "title": "Dashboard", "page": "pages/1_📊_Dashboard.py"},
    {"emoji": "📈", "title": "Relatórios", "page": "pages/5_📈_Relatórios.py"}
]
for i, card in enumerate(cards):
    with [col1, col2, col3, col4][i]:
        if st.button(f"{card['emoji']} {card['title']}", use_container_width=True):
            st.switch_page(card['page'])

st.markdown("---")
st.subheader("📋 Últimas Transações")
try:
    # Load a small list of the most recent transactions for this user.
    recent_transactions = transactions_service.get_recent_transactions(telegram_id, limit=5)
    if recent_transactions:
        for t in recent_transactions:
            emoji = "💰" if t.type == "renda" else "💸" if "despesa" in t.type else "🚀"
            col_emoji, col_desc, col_value = st.columns([1, 4, 2])
            with col_emoji: st.write(emoji)
            with col_desc: st.write(f"**{t.description}**\n📅 {t.date.strftime('%d/%m/%Y')} | 📂 {t.category}")
            with col_value: st.write(f"R$ {t.amount:,.2f}")
        st.markdown("---")
    else:
        st.info("Nenhuma transação recente encontrada.")
except Exception as e:
    st.error(f"Erro ao carregar transações: {e}")