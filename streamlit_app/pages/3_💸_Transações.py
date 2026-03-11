import streamlit as st
import pandas as pd
from datetime import date
from services.transactions_service import transactions_service
from services.ai_processor import ai_processor # Para as categorias
from utils import check_authentication

st.set_page_config(page_title="Transações", page_icon="💸", layout="wide")

# --- Authentication and page state ---
telegram_id = check_authentication()

# Track which transaction is being edited and the current pagination page.
if 'editing_transaction_id' not in st.session_state:
    st.session_state.editing_transaction_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

st.markdown('<h1 class="main-header">💸 Gerenciar Transações</h1>', unsafe_allow_html=True)

# ==============================================================================
# Block 1: Create / Edit form
# ==============================================================================
def show_transaction_form(transaction_to_edit=None):
    """Render a form to create a new transaction or edit an existing one."""
    is_editing = transaction_to_edit is not None
    title = "✏️ Editar Transação" if is_editing else "➕ Adicionar Nova Transação"
    
    with st.expander(title, expanded=is_editing):
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                description = st.text_input("Descrição*", value=transaction_to_edit.description if is_editing else "")
                amount = st.number_input("Valor (R$)*", min_value=0.01, step=0.01, value=float(transaction_to_edit.amount) if is_editing else 0.1)
            with col2:
                category = st.selectbox("Categoria*", list(ai_processor.categories.keys()), index=list(ai_processor.categories.keys()).index(transaction_to_edit.category) if is_editing else 0)
                type_ = st.selectbox("Tipo*", ["renda", "despesa_fixa", "despesa_variavel", "economia"], index=["renda", "despesa_fixa", "despesa_variavel", "economia"].index(transaction_to_edit.type) if is_editing else 2)
                trans_date = st.date_input("Data*", value=transaction_to_edit.date if is_editing else date.today())
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("💾 Salvar", use_container_width=True)
            with col_cancel:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.editing_transaction_id = None
                    st.rerun()

            if submitted:
                if not description or amount <= 0:
                    st.error("Descrição e Valor são obrigatórios.")
                    return

                if is_editing:
                    success = transactions_service.update(
                        transaction_to_edit.id,
                        description=description,
                        amount=amount,
                        category=category,
                        type=type_,
                        date=trans_date
                    )
                    if success:
                        st.success("✅ Transação atualizada com sucesso!")
                        st.session_state.editing_transaction_id = None
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar a transação.")
                else:
                    new_transaction = transactions_service.create(
                        telegram_id,
                        description,
                        amount,
                        category,
                        type_,
                        trans_date
                    )
                    if new_transaction:
                        st.success("✅ Transação criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao criar a transação.")


# If we have an ID in session_state, load that transaction and show the edit form.
if st.session_state.editing_transaction_id:
    transaction_to_edit = transactions_service.get_by_id(st.session_state.editing_transaction_id)
    if transaction_to_edit:
        show_transaction_form(transaction_to_edit)
    else:
        st.error("Transação não encontrada.")
        st.session_state.editing_transaction_id = None
else:
    # Default view: show the create form.
    show_transaction_form()

st.markdown("---")


# ==============================================================================
# Block 2: Filters and transaction list
# ==============================================================================
with st.expander("🔍 Filtros Avançados", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_term = st.text_input("Buscar descrição")
    with col2:
        category_filter = st.selectbox("Categoria", ["Todas"] + list(ai_processor.categories.keys()))
    with col3:
        type_filter = st.selectbox("Tipo", ["Todos", "renda", "despesa_fixa", "despesa_variavel", "economia"])
    with col4:
        date_range = st.selectbox("Período", ["7_days","30_days","90_days","current_month","last_month","all_time"])
    
    sort_by = st.selectbox("Ordenar por", ["date_desc","date_asc","amount_desc","amount_asc","description_asc"])
    items_per_page = st.selectbox("Itens por página", [25, 50, 100], index=0)

filters = {
    "search_term": search_term,
    "category": category_filter,
    "type": type_filter,
    "date_range": date_range,
    "sort_by": sort_by
}

# Fetch transactions from the service using the current filters and page.
transactions, total_pages = transactions_service.get_transactions(
    telegram_id=telegram_id,
    filters=filters,
    page=st.session_state.current_page,
    items_per_page=items_per_page
)

# Render the transaction list.
if transactions:
    for t in transactions:
        with st.container():
            col_info, col_actions = st.columns([4, 1])
            
            with col_info:
                emoji = "💰" if t.type == "renda" else "💸" if "despesa" in t.type else "🚀"
                st.markdown(f"**{emoji} {t.description}**")
                st.caption(f"📅 {t.date.strftime('%d/%m/%Y')} | 📂 {t.category} | {t.type.replace('_', ' ').title()}")
                st.markdown(f"**Valor:** R$ {t.amount:,.2f}")
            
            with col_actions:
                st.write("")  # Simple vertical spacing.
                if st.button("✏️", key=f"edit_{t.id}", help="Editar"):
                    st.session_state.editing_transaction_id = t.id
                    st.rerun()
                if st.button("🗑️", key=f"delete_{t.id}", help="Excluir"):
                    if transactions_service.delete(t.id):
                        st.success("✅ Transação excluída!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir.")
            
            st.markdown("---")
else:
    st.info("Nenhuma transação encontrada com os filtros selecionados.")


# ==============================================================================
# Block 3: Pagination
# ==============================================================================
if total_pages > 1:
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        if st.button("⏮️", disabled=st.session_state.current_page == 0):
            st.session_state.current_page = 0
            st.rerun()
    with col2:
        if st.button("◀️", disabled=st.session_state.current_page == 0):
            st.session_state.current_page = max(0, st.session_state.current_page - 1)
            st.rerun()
    with col3:
        st.markdown(f"<div style='text-align: center; padding-top: 13px;'>**Página {st.session_state.current_page + 1} de {total_pages}**</div>", unsafe_allow_html=True)
    with col4:
        if st.button("▶️", disabled=st.session_state.current_page >= total_pages - 1):
            st.session_state.current_page = min(total_pages - 1, st.session_state.current_page + 1)
            st.rerun()
    with col5:
        if st.button("⏭️", disabled=st.session_state.current_page >= total_pages - 1):
            st.session_state.current_page = total_pages - 1
            st.rerun()