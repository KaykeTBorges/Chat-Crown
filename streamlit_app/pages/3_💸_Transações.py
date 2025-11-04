# pages/3_💸_Transações.py
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.transactions_service import transactions_service

st.set_page_config(page_title="Transações", page_icon="💸", layout="wide")

# ---------------- CSS personalizado ----------------
st.markdown("""
<style>
    .transaction-row {background-color:#f8f9fa;padding:1rem;border-radius:8px;border-left:4px solid #1f77b4;margin:0.5rem 0;transition: all 0.3s ease;}
    .transaction-row:hover {background-color:#e9ecef;transform:translateX(5px);}
    .compact-view {padding:0.5rem;margin:0.25rem 0;border-radius:5px;border-left:3px solid;}
    .income { border-left-color: #28a745; background-color: #d4edda; }
    .expense { border-left-color: #dc3545; background-color: #f8d7da; }
    .economy { border-left-color: #007bff; background-color: #cce7ff; }
</style>
""", unsafe_allow_html=True)

# ---------------- Inicialização ----------------
user_id = st.session_state.user_id
if "editing_transaction_id" not in st.session_state:
    st.session_state.editing_transaction_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

st.markdown('<h1 class="main-header">💸 Gerenciar Transações</h1>', unsafe_allow_html=True)

# ---------------- Filtros ----------------
with st.expander("🔍 Filtros Avançados", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_term = st.text_input("Buscar descrição")
    with col2:
        category = st.selectbox("Categoria", ["Todas"] + list(transactions_service.categories.keys()))
    with col3:
        type_filter = st.selectbox("Tipo", ["Todos", "renda", "despesa_fixa", "despesa_variavel", "economia"])
    with col4:
        date_range = st.selectbox("Período", ["7_days","30_days","90_days","current_month","last_month","all_time"])

    sort_by = st.selectbox("Ordenar por", ["date_desc","date_asc","amount_desc","amount_asc","description_asc"])
    items_per_page = st.selectbox("Itens por página", [25,50,100,200], index=0)

filters = {
    "search_term": search_term,
    "category": category,
    "type": type_filter,
    "date_range": date_range,
    "sort_by": sort_by
}

# ---------------- Buscar transações ----------------
transactions, total_pages = transactions_service.get_transactions(
    user_id=user_id,
    filters=filters,
    page=st.session_state.current_page,
    items_per_page=items_per_page
)

# ---------------- Mostrar transações ----------------
view_mode = st.radio("Modo de visualização", ["📋 Detalhado","📱 Compacto"], horizontal=True)

if view_mode == "📱 Compacto":
    for t in transactions:
        css_class = "income" if t.type=="renda" else "expense" if "despesa" in t.type else "economy"
        emoji = "💰" if t.type=="renda" else "💸" if "despesa" in t.type else "🚀"
        st.markdown(f'<div class="compact-view {css_class}">', unsafe_allow_html=True)
        st.write(f"{emoji} {t.description} | {t.category} | {t.date.strftime('%d/%m/%Y')} | R$ {t.amount:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    for t in transactions:
        st.markdown(f'<div class="transaction-row">', unsafe_allow_html=True)
        st.write(f"📅 {t.date.strftime('%d/%m/%Y')} | {t.type} | {t.category} | {t.description} | R$ {t.amount:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Paginação ----------------
col1, col2, col3, col4, col5 = st.columns([1,1,2,1,1])
with col1:
    if st.button("⏮️ Primeira", disabled=st.session_state.current_page==0):
        st.session_state.current_page=0
        st.rerun()
with col2:
    if st.button("◀️ Anterior", disabled=st.session_state.current_page==0):
        st.session_state.current_page=max(0, st.session_state.current_page-1)
        st.rerun()
with col3:
    st.markdown(f"**Página {st.session_state.current_page+1} de {total_pages}**")
with col4:
    if st.button("Próxima ▶️", disabled=st.session_state.current_page>=total_pages-1):
        st.session_state.current_page=min(total_pages-1, st.session_state.current_page+1)
        st.rerun()
with col5:
    if st.button("Última ⏭️", disabled=st.session_state.current_page>=total_pages-1):
        st.session_state.current_page=total_pages-1
        st.rerun()

# ---------------- Importar ----------------
st.markdown("---")
st.subheader("📥 Importar Dados (CSV ou Excel)")
uploaded_file = st.file_uploader("Arquivo", type=["csv","xlsx","xls"])
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        else:
            df = pd.read_excel(uploaded_file)
        df.columns = [c.lower().strip() for c in df.columns]

        if st.button("✅ Importar agora"):
            success = transactions_service.import_from_dataframe(user_id, df)
            if success:
                st.success("🎉 Importado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao importar.")
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

# ---------------- Exportar ----------------
st.markdown("---")
st.subheader("📤 Exportar Dados")
if transactions:
    csv_data = transactions_service.export(transactions, "csv")
    json_data = transactions_service.export(transactions, "json")
    st.download_button("📥 CSV", csv_data, f"transacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    st.download_button("📄 JSON", json_data, f"transacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
