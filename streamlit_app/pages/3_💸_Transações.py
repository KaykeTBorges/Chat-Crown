import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.database import db_manager
from services.ai_processor import ai_processor

st.set_page_config(page_title="Transações", page_icon="💸", layout="wide")

class TransactionsPage:
    def __init__(self):
        self.user_id = 1
    
    def show_transactions(self):
        st.markdown('<h1 class="main-header">💸 Gerenciar Transações</h1>', unsafe_allow_html=True)
        
        # Inicializar estado de edição se não existir
        if 'editing_transaction_id' not in st.session_state:
            st.session_state.editing_transaction_id = None
        
        # Se estiver editando, mostrar formulário
        if st.session_state.editing_transaction_id:
            self._show_edit_form(st.session_state.editing_transaction_id)
            return
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="trans_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="trans_year")
        
        # Buscar transações
        transacoes = self._get_monthly_transactions(mes, ano)
        
        # Estatísticas rápidas
        if transacoes:
            total_transacoes = len(transacoes)
            ultima_transacao = max(transacoes, key=lambda x: x.date)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Transações", total_transacoes)
            with col2:
                st.metric("Período", f"{mes:02d}/{ano}")
            with col3:
                st.metric("Última Transação", ultima_transacao.date.strftime("%d/%m/%Y"))
        
        # Tabela de transações
        st.subheader("📋 Todas as Transações")
        
        if transacoes:
            # Filtros adicionais
            col1, col2 = st.columns(2)
            with col1:
                tipos = list(set([t.type for t in transacoes]))
                filtro_tipo = st.selectbox("Filtrar por tipo:", ["Todos"] + tipos)
            with col2:
                categorias = list(set([t.category for t in transacoes]))
                filtro_categoria = st.selectbox("Filtrar por categoria:", ["Todas"] + categorias)
            
            # Aplicar filtros
            transacoes_filtradas = transacoes
            if filtro_tipo != "Todos":
                transacoes_filtradas = [t for t in transacoes_filtradas if t.type == filtro_tipo]
            if filtro_categoria != "Todas":
                transacoes_filtradas = [t for t in transacoes_filtradas if t.category == filtro_categoria]
            
            # Mostrar cada transação com opções de edição
            for transacao in transacoes_filtradas:
                self._render_transaction_row(transacao)
            
            # Opções de exportação
            df = pd.DataFrame([{
                'Data': t.date.strftime("%d/%m/%Y"),
                'Tipo': t.type,
                'Categoria': t.category,
                'Descrição': t.description,
                'Valor': t.amount,
                'Detectado por': t.detected_by
            } for t in transacoes_filtradas])
            
            st.download_button(
                label="📥 Exportar para CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"transacoes_{mes:02d}_{ano}.csv",
                mime="text/csv"
            )
        else:
            st.info("📝 Nenhuma transação encontrada para este período.")
    
    def _get_monthly_transactions(self, mes, ano):
        """Busca transações do mês específico"""
        try:
            with db_manager.get_session() as session:
                from models.transaction import Transaction
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == self.user_id,
                    Transaction.date >= f"{ano}-{mes:02d}-01",
                    Transaction.date <= f"{ano}-{mes:02d}-{self._dias_no_mes(mes, ano)}"
                ).order_by(Transaction.date.desc()).all()
                return transactions
        except Exception as e:
            st.error(f"Erro ao buscar transações: {e}")
            return []
    
    def _dias_no_mes(self, month, year):
        """Retorna número de dias no mês"""
        if month == 12:
            return (datetime(year + 1, 1, 1) - datetime(year, month, 1)).days
        return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
    
    def _render_transaction_row(self, transacao):
        """Renderiza uma linha de transação com botões de ação"""
        emoji = self._get_emoji_for_category(transacao.category)
        tipo_texto = self._get_type_text(transacao.type)
        valor_color = "#10B981" if transacao.type == 'renda' else "#EF4444" if 'despesa' in transacao.type else "#3B82F6"
        
        st.markdown(f'<div class="transaction-row">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 3, 2, 2])
        
        with col1:
            st.write(f"**{transacao.date.strftime('%d/%m/%Y')}**")
        
        with col2:
            st.write(tipo_texto)
        
        with col3:
            st.write(f"{emoji} {transacao.category}")
        
        with col4:
            st.write(transacao.description)
        
        with col5:
            st.markdown(f"<span style='color: {valor_color}; font-weight: bold;'>R$ {transacao.amount:,.2f}</span>", unsafe_allow_html=True)
        
        with col6:
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️ Editar", key=f"edit_{transacao.id}", use_container_width=True):
                    st.session_state.editing_transaction_id = transacao.id
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{transacao.id}", use_container_width=True):
                    if db_manager.delete_transaction(transacao.id):
                        st.success("✅ Transação excluída!")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _show_edit_form(self, transaction_id):
        """Mostra formulário de edição"""
        st.markdown('<div class="edit-form">', unsafe_allow_html=True)
        
        # Botão voltar
        if st.button("← Voltar para lista"):
            st.session_state.editing_transaction_id = None
            st.rerun()
        
        st.subheader("✏️ Editar Transação")
        
        # Buscar transação
        transacao = db_manager.get_transaction_by_id(transaction_id)
        
        if not transacao:
            st.error("❌ Transação não encontrada")
            st.session_state.editing_transaction_id = None
            st.rerun()
            return
        
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