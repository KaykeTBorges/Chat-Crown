import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.database import db_manager
from services.ai_processor import ai_processor
from services.transactions_service import transactions_service

st.set_page_config(page_title="Transações", page_icon="💸", layout="wide")

# CSS melhorado para UX
st.markdown("""
<style>
    .transaction-row {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .transaction-row:hover {
        background-color: #e9ecef;
        transform: translateX(5px);
    }
    .edit-form {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .quick-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .compact-view {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 3px solid;
    }
    .income { border-left-color: #28a745; background-color: #d4edda; }
    .expense { border-left-color: #dc3545; background-color: #f8d7da; }
    .economy { border-left-color: #007bff; background-color: #cce7ff; }
</style>
""", unsafe_allow_html=True)

class TransactionsPage:
    def __init__(self):
        self.user_id = 1
    
    def show_transactions(self):
        st.markdown('<h1 class="main-header">💸 Gerenciar Transações</h1>', unsafe_allow_html=True)
        
        # Inicializar estados da sessão
        self._initialize_session_state()
        
        # Se estiver editando, mostrar formulário
        if st.session_state.editing_transaction_id:
            self._show_edit_form(st.session_state.editing_transaction_id)
            return
        
        # Controles de visualização
        col1, col2 = st.columns([3, 1])
        with col1:
            view_mode = st.radio(
                "Modo de Visualização:",
                ["📋 Detalhado", "📱 Compacto"],
                horizontal=True,
                key="view_mode"
            )
        with col2:
            items_per_page = st.selectbox(
                "Itens por página:",
                [25, 50, 100, 200],
                index=0,
                key="items_per_page"
            )
        
        # Seção de filtros avançados
        self._show_advanced_filters()
        
        # Buscar e mostrar transações
        transacoes_filtradas = self._get_filtered_transactions()
        
        # Estatísticas rápidas
        self._show_quick_stats(transacoes_filtradas)
        
        # Paginação
        transacoes_paginadas = self._apply_pagination(transacoes_filtradas, items_per_page)
        
        # Mostrar transações
        if transacoes_paginadas:
            if view_mode == "📱 Compacto":
                self._render_compact_view(transacoes_paginadas)
            else:
                self._render_detailed_view(transacoes_paginadas)
            
            # Controles de paginação
            self._show_pagination_controls(transacoes_filtradas, items_per_page)
            
            # Exportação
            self._show_export_options(transacoes_filtradas)
        else:
            st.info("🔍 Nenhuma transação encontrada com os filtros atuais.")
    
    def _initialize_session_state(self):
        """Inicializa todos os estados da sessão necessários"""
        defaults = {
            'editing_transaction_id': None,
            'current_page': 0,
            'search_term': '',
            'filter_category': 'Todas',
            'filter_type': 'Todos',
            'filter_date_range': '30_days',
            'sort_by': 'date_desc'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _show_advanced_filters(self):
        """Mostra seção de filtros avançados"""
        with st.expander("🔍 Filtros Avançados", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Busca por texto
                st.session_state.search_term = st.text_input(
                    "Buscar na descrição",
                    value=st.session_state.search_term,
                    placeholder="Ex: almoço, uber, mercado..."
                )
            
            with col2:
                # Filtro por categoria
                categories = ['Todas'] + list(ai_processor.categories.keys())
                st.session_state.filter_category = st.selectbox(
                    "Categoria",
                    categories,
                    index=categories.index(st.session_state.filter_category)
                )
            
            with col3:
                # Filtro por tipo
                types = ['Todos', 'renda', 'despesa_fixa', 'despesa_variavel', 'economia']
                st.session_state.filter_type = st.selectbox(
                    "Tipo",
                    types,
                    index=types.index(st.session_state.filter_type)
                )
            
            with col4:
                # Filtro por período
                date_ranges = {
                    '7_days': 'Últimos 7 dias',
                    '30_days': 'Últimos 30 dias',
                    '90_days': 'Últimos 3 meses',
                    'current_month': 'Este mês',
                    'last_month': 'Mês anterior',
                    'all_time': 'Todo período'
                }
                st.session_state.filter_date_range = st.selectbox(
                    "Período",
                    list(date_ranges.keys()),
                    format_func=lambda x: date_ranges[x],
                    index=list(date_ranges.keys()).index(st.session_state.filter_date_range)
                )
            
            # Ordenação
            col5, col6 = st.columns(2)
            with col5:
                sort_options = {
                    'date_desc': 'Data (Mais Recente)',
                    'date_asc': 'Data (Mais Antiga)',
                    'amount_desc': 'Valor (Maior)',
                    'amount_asc': 'Valor (Menor)',
                    'description_asc': 'Descrição (A-Z)'
                }
                st.session_state.sort_by = st.selectbox(
                    "Ordenar por",
                    list(sort_options.keys()),
                    format_func=lambda x: sort_options[x],
                    index=list(sort_options.keys()).index(st.session_state.sort_by)
                )
            
            with col6:
                # Botões de ação rápida
                col_reset, col_apply = st.columns(2)
                with col_reset:
                    if st.button("🔄 Limpar Filtros", use_container_width=True):
                        self._reset_filters()
                with col_apply:
                    if st.button("💾 Aplicar Filtros", use_container_width=True, type="primary"):
                        st.rerun()
    
    def _reset_filters(self):
        """Reseta todos os filtros para os valores padrão"""
        st.session_state.search_term = ''
        st.session_state.filter_category = 'Todas'
        st.session_state.filter_type = 'Todos'
        st.session_state.filter_date_range = '30_days'
        st.session_state.sort_by = 'date_desc'
        st.session_state.current_page = 0
        st.rerun()
    
    def _get_filtered_transactions(self):
        """Busca e filtra transações baseado nos critérios atuais"""
        # Buscar todas as transações (sem limite)
        all_transactions = self._get_all_transactions()
        
        if not all_transactions:
            return []
        
        # Aplicar filtros
        filtered = all_transactions
        
        # Filtro de busca textual
        if st.session_state.search_term:
            search_lower = st.session_state.search_term.lower()
            filtered = [t for t in filtered if search_lower in t.description.lower()]
        
        # Filtro de categoria
        if st.session_state.filter_category != 'Todas':
            filtered = [t for t in filtered if t.category == st.session_state.filter_category]
        
        # Filtro de tipo
        if st.session_state.filter_type != 'Todos':
            filtered = [t for t in filtered if t.type == st.session_state.filter_type]
        
        # Filtro de data
        filtered = self._apply_date_filter(filtered)
        
        # Ordenação
        filtered = self._apply_sorting(filtered)
        
        return filtered
    
    def _get_all_transactions(self):
        """Busca todas as transações do usuário"""
        try:
            with db_manager.get_session() as session:
                from models.transaction import Transaction
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == self.user_id
                ).all()
                return transactions
        except Exception as e:
            st.error(f"Erro ao buscar transações: {e}")
            return []
    
    def _apply_date_filter(self, transactions):
        """Aplica filtro de data baseado na seleção"""
        today = datetime.now().date()
        
        date_ranges = {
            '7_days': today - timedelta(days=7),
            '30_days': today - timedelta(days=30),
            '90_days': today - timedelta(days=90),
            'current_month': today.replace(day=1),
            'last_month': (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            'all_time': datetime.min.date()
        }
        
        start_date = date_ranges.get(st.session_state.filter_date_range, datetime.min.date())
        
        filtered = []
        for transaction in transactions:
            transaction_date = transaction.date
            if isinstance(transaction_date, str):
                transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            if transaction_date >= start_date:
                filtered.append(transaction)
        
        return filtered
    
    def _apply_sorting(self, transactions):
        """Aplica ordenação baseada na seleção"""
        sort_functions = {
            'date_desc': lambda x: x.date if isinstance(x.date, datetime) else datetime.strptime(x.date, '%Y-%m-%d'),
            'date_asc': lambda x: x.date if isinstance(x.date, datetime) else datetime.strptime(x.date, '%Y-%m-%d'),
            'amount_desc': lambda x: x.amount,
            'amount_asc': lambda x: x.amount,
            'description_asc': lambda x: x.description.lower()
        }
        
        sort_func = sort_functions.get(st.session_state.sort_by, sort_functions['date_desc'])
        reverse = st.session_state.sort_by in ['date_desc', 'amount_desc']
        
        return sorted(transactions, key=sort_func, reverse=reverse)
    
    def _apply_pagination(self, transactions, items_per_page):
        """Aplica paginação às transações"""
        start_idx = st.session_state.current_page * items_per_page
        end_idx = start_idx + items_per_page
        return transactions[start_idx:end_idx]
    
    def _show_quick_stats(self, transactions):
        """Mostra estatísticas rápidas sobre as transações filtradas"""
        if not transactions:
            return
        
        total_count = len(transactions)
        total_amount = sum(t.amount for t in transactions)
        income_amount = sum(t.amount for t in transactions if t.type == 'renda')
        expense_amount = sum(t.amount for t in transactions if t.type in ['despesa_fixa', 'despesa_variavel'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Transações", total_count)
        
        with col2:
            st.metric("Valor Total", f"R$ {total_amount:,.2f}")
        
        with col3:
            st.metric("Renda", f"R$ {income_amount:,.2f}")
        
        with col4:
            st.metric("Despesas", f"R$ {expense_amount:,.2f}")
    
    def _render_compact_view(self, transactions):
        """Renderiza visualização compacta das transações"""
        st.subheader(f"📱 Visualização Compacta ({len(transactions)} transações)")
        
        for transaction in transactions:
            # Determinar classe CSS baseada no tipo
            if transaction.type == 'renda':
                css_class = "income"
                emoji = "💰"
            elif transaction.type in ['despesa_fixa', 'despesa_variavel']:
                css_class = "expense"
                emoji = "💸"
            else:
                css_class = "economy"
                emoji = "🚀"
            
            with st.container():
                st.markdown(f'<div class="compact-view {css_class}">', unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{emoji} {transaction.description}**")
                    st.caption(f"📅 {transaction.date.strftime('%d/%m/%Y')} | 📂 {transaction.category}")
                
                with col2:
                    tipo_texto = self._get_type_text(transaction.type)
                    st.write(tipo_texto)
                
                with col3:
                    valor_color = "#28a745" if transaction.type == 'renda' else "#dc3545" if 'despesa' in transaction.type else "#007bff"
                    st.markdown(f"<span style='color: {valor_color}; font-weight: bold;'>R$ {transaction.amount:,.2f}</span>", unsafe_allow_html=True)
                
                with col4:
                    if st.button("✏️", key=f"edit_compact_{transaction.id}", help="Editar"):
                        st.session_state.editing_transaction_id = transaction.id
                        st.rerun()
                
                with col5:
                    if st.button("🗑️", key=f"delete_compact_{transaction.id}", help="Excluir"):
                        if db_manager.delete_transaction(transaction.id):
                            st.success("✅ Transação excluída!")
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_detailed_view(self, transactions):
        """Renderiza visualização detalhada das transações"""
        st.subheader(f"📋 Visualização Detalhada ({len(transactions)} transações)")
        
        for transaction in transactions:
            self._render_transaction_row(transaction)
    
    def _render_transaction_row(self, transaction):
        """Renderiza uma linha de transação na visualização detalhada"""
        emoji = self._get_emoji_for_category(transaction.category)
        tipo_texto = self._get_type_text(transaction.type)
        valor_color = "#28a745" if transaction.type == 'renda' else "#dc3545" if 'despesa' in transaction.type else "#007bff"
        
        st.markdown(f'<div class="transaction-row">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 2, 1.5, 1])
        
        with col1:
            st.write(f"**{transaction.date.strftime('%d/%m/%Y')}**")
            st.caption("📅 Data")
        
        with col2:
            st.write(tipo_texto)
            st.caption("📊 Tipo")
        
        with col3:
            st.write(f"{emoji} {transaction.category}")
            st.caption("📂 Categoria")
        
        with col4:
            st.write(transaction.description)
            st.caption("📝 Descrição")
        
        with col5:
            st.markdown(f"<span style='color: {valor_color}; font-weight: bold;'>R$ {transaction.amount:,.2f}</span>", unsafe_allow_html=True)
            st.caption("💳 Valor")
        
        with col6:
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{transaction.id}", help="Editar transação", use_container_width=True):
                    st.session_state.editing_transaction_id = transaction.id
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{transaction.id}", help="Excluir transação", use_container_width=True):
                    if db_manager.delete_transaction(transaction.id):
                        st.success("✅ Transação excluída!")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _show_pagination_controls(self, all_transactions, items_per_page):
        """Mostra controles de paginação"""
        total_pages = max(1, (len(all_transactions) + items_per_page - 1) // items_per_page)
        current_page = st.session_state.current_page
        
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ Primeira", disabled=current_page == 0, use_container_width=True):
                    st.session_state.current_page = 0
                    st.rerun()
            
            with col2:
                if st.button("◀️ Anterior", disabled=current_page == 0, use_container_width=True):
                    st.session_state.current_page = max(0, current_page - 1)
                    st.rerun()
            
            with col3:
                st.markdown(f"**Página {current_page + 1} de {total_pages}**", unsafe_allow_html=True)
                st.caption(f"Mostrando {len(self._apply_pagination(all_transactions, items_per_page))} de {len(all_transactions)} transações")
            
            with col4:
                if st.button("Próxima ▶️", disabled=current_page >= total_pages - 1, use_container_width=True):
                    st.session_state.current_page = min(total_pages - 1, current_page + 1)
                    st.rerun()
            
            with col5:
                if st.button("Última ⏭️", disabled=current_page >= total_pages - 1, use_container_width=True):
                    st.session_state.current_page = total_pages - 1
                    st.rerun()

    def _show_import_section(self):
        """Mostra área de importação de planilhas"""
        st.markdown("---")
        st.subheader("📥 Importar Dados (CSV ou Excel)")

        uploaded_file = st.file_uploader(
            "Selecione um arquivo",
            type=["csv", "xlsx", "xls"],
            help="O arquivo deve conter colunas: data, descricao, valor, categoria, tipo"
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                else:
                    df = pd.read_excel(uploaded_file)

                # Normalizar nomes de colunas
                df.columns = [c.lower().strip() for c in df.columns]

                # Validar colunas obrigatórias
                required = {"data", "descricao", "valor", "categoria", "tipo"}
                if not required.issubset(set(df.columns)):
                    st.error("❌ O arquivo precisa conter as colunas: data, descricao, valor, categoria, tipo")
                    return

                # Preview
                st.write("Pré-visualização dos dados:")
                st.dataframe(df.head())

                if st.button("✅ Importar agora"):
                    with db_manager.get_session() as session:
                        from models.transaction import Transaction
                        for _, row in df.iterrows():
                            session.add(Transaction(
                                user_id=self.user_id,
                                description=row["descricao"],
                                amount=float(row["valor"]),
                                category=row["categoria"],
                                type=row["tipo"],
                                date=pd.to_datetime(row["data"]).date(),
                                detected_by="upload"
                            ))
                        session.commit()

                    st.success("🎉 Importação concluída com sucesso!")
                    st.rerun()

            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

    
    def _show_export_options(self, transactions):
        """Mostra opções de exportação"""
        st.markdown("---")
        st.subheader("📤 Exportar Dados")
        
        if transactions:
            col1, col2 = st.columns(2)
            
            with col1:
                # Exportar para CSV
                df = pd.DataFrame([{
                    'Data': t.date.strftime("%d/%m/%Y"),
                    'Tipo': t.type,
                    'Categoria': t.category,
                    'Descrição': t.description,
                    'Valor': t.amount,
                    'Detectado por': t.detected_by
                } for t in transactions])
                
                st.download_button(
                    label="📥 Exportar para CSV",
                    data=df.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name=f"transacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Exportar para JSON
                json_data = {
                    'export_date': datetime.now().isoformat(),
                    'total_transactions': len(transactions),
                    'transactions': [
                        {
                            'id': t.id,
                            'description': t.description,
                            'amount': float(t.amount),
                            'category': t.category,
                            'type': t.type,
                            'date': t.date.isoformat(),
                            'detected_by': t.detected_by
                        } for t in transactions
                    ]
                }
                
                st.download_button(
                    label="📄 Exportar para JSON",
                    data=pd.Series([json_data]).to_json(orient='records').encode('utf-8'),
                    file_name=f"transacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("Nenhuma transação para exportar.")
    
    def _show_edit_form(self, transaction_id):
        """Mostra formulário de edição"""
        st.markdown('<div class="edit-form">', unsafe_allow_html=True)
        
        # Botão voltar
        if st.button("← Voltar para lista"):
            st.session_state.editing_transaction_id = None
            st.rerun()
        
        st.subheader("✏️ Editar Transação")
        
        # Buscar transação
        transacao = transactions_service.get_by_id(transaction_id)
        
        if transactions_service.update(
            transaction_id,
            description=nova_descricao,
            amount=novo_valor,
            category=nova_categoria,
            type=novo_tipo,
            date=nova_data
        ):
            st.success("✅ Transação atualizada!")
            st.session_state.editing_transaction_id = None
            st.rerun()

        if transactions_service.delete(transaction_id):
            st.success("✅ Transação excluída!")
            st.rerun()
        
        # Formulário de edição
        with st.form(f"edit_form_{transaction_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                nova_descricao = st.text_input("Descrição", value=transacao.description)
                novo_valor = st.number_input("Valor (R$)", value=float(transacao.amount), min_value=0.01, step=0.01)
            
            with col2:
                categorias = list(ai_processor.categories.keys())
                categoria_index = categorias.index(transacao.category) if transacao.category in categorias else 0
                nova_categoria = st.selectbox("Categoria", categorias, index=categoria_index)
                
                tipos = ["renda", "despesa_fixa", "despesa_variavel", "economia"]
                tipo_index = tipos.index(transacao.type)
                novo_tipo = st.selectbox("Tipo", tipos, index=tipo_index)
            
            # Data
            data_transacao = transacao.date
            if isinstance(data_transacao, str):
                data_transacao = datetime.strptime(data_transacao, '%Y-%m-%d').date()
            nova_data = st.date_input("Data", value=data_transacao)
            
            col_salvar, col_cancelar = st.columns(2)
            
            with col_salvar:
                if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    if db_manager.update_transaction(
                        transaction_id,
                        description=nova_descricao,
                        amount=novo_valor,
                        category=nova_categoria,
                        type=novo_tipo,
                        date=nova_data
                    ):
                        st.success("✅ Transação atualizada com sucesso!")
                        st.session_state.editing_transaction_id = None
                        st.rerun()
            
            with col_cancelar:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.editing_transaction_id = None
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _get_emoji_for_category(self, category):
        """Retorna emoji para categoria"""
        emoji_map = {
            'Salário': '💰', 'Freela': '💼', 'Investimentos': '📈', 'Outros': '🎯',
            'Moradia': '🏠', 'Transporte': '🚗', 'Saúde': '💊', 'Educação': '📚',
            'Seguros': '🛡️', 'Dívidas': '💳', 'Alimentação': '🍽️', 'Lazer': '🎮',
            'Vestuário': '👕', 'Diversos': '📦', 'Investimentos': '🚀', 'Poupança': '🐷',
            'Fundos': '📊', 'Previdência': '👵'
        }
        return emoji_map.get(category, '💸')
    
    def _get_type_text(self, transaction_type):
        """Retorna texto amigável para tipo"""
        type_map = {
            'renda': '💰 Renda',
            'despesa_fixa': '🔴 Despesa Fixa',
            'despesa_variavel': '🟡 Despesa Variável',
            'economia': '🚀 Economia'
        }
        return type_map.get(transaction_type, transaction_type)

# Instância e execução
transactions_page = TransactionsPage()
transactions_page.show_transactions()