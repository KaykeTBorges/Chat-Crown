import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.goal_service import goal_service

st.set_page_config(page_title="Metas Financeiras", page_icon="🎯", layout="wide")

class GoalsPage:
    def __init__(self):
        self.user_id = 1
    
    def show_goals(self):
        st.markdown('<h1 class="main-header">🎯 Metas Financeiras</h1>', unsafe_allow_html=True)
        
        # Inicializar estado se não existir
        if 'editing_goal_id' not in st.session_state:
            st.session_state.editing_goal_id = None
        
        if st.session_state.editing_goal_id:
            self._show_edit_goal_form(st.session_state.editing_goal_id)
        else:
            self._show_goals_list()
    
    def _show_goals_list(self):
        """Mostra a lista de metas com opção de adicionar nova"""
        
        # Formulário para nova meta
        with st.expander("🎯 Adicionar Nova Meta", expanded=False):
            with st.form("new_goal_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Nome da Meta*", placeholder="Ex: Viagem para Europa")
                    target_amount = st.number_input("Valor Alvo (R$)*", min_value=0.01, step=100.0, value=1000.0)
                    category = st.selectbox("Categoria", 
                                          ["Viagem", "Reserva Emergencial", "Investimento", 
                                           "Estudos", "Casa", "Carro", "Outros"])
                
                with col2:
                    deadline = st.date_input("Data Limite*", 
                                           min_value=date.today() + timedelta(days=1),
                                           value=date.today() + timedelta(days=365))
                    priority = st.select_slider("Prioridade", options=[1, 2, 3, 4, 5], value=3)
                    current_amount = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0, value=0.0)
                
                if st.form_submit_button("🎯 Criar Meta", use_container_width=True):
                    if name and target_amount > 0:
                        if goal_service.create_goal(
                            user_id=self.user_id,
                            name=name,
                            target_amount=target_amount,
                            deadline=deadline.strftime('%Y-%m-%d'),
                            category=category,
                            priority=priority
                        ):
                            # Se foi informado valor atual, atualizar progresso
                            if current_amount > 0:
                                goals = goal_service.get_user_goals(self.user_id)
                                if goals:
                                    goal_service.update_goal_progress(goals[0]['id'], current_amount)
                            
                            st.success("✅ Meta criada com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao criar meta")
                    else:
                        st.warning("⚠️ Preencha todos os campos obrigatórios")
        
        # Lista de metas
        st.subheader("📈 Minhas Metas")
        
        goals = goal_service.get_user_goals(self.user_id)
        
        if not goals:
            st.info("🎯 Você ainda não tem metas definidas. Crie sua primeira meta acima!")
            return
        
        # Estatísticas rápidas
        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g['progress_percentage'] >= 100)
        total_target = sum(g['target_amount'] for g in goals)
        total_current = sum(g['current_amount'] for g in goals)
        overall_progress = (total_current / total_target * 100) if total_target > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Metas", total_goals)
        with col2:
            st.metric("Concluídas", completed_goals)
        with col3:
            st.metric("Progresso Total", f"{overall_progress:.1f}%")
        with col4:
            st.metric("Valor Total", f"R$ {total_target:,.2f}")
        
        # Gráfico de progresso geral
        fig = self._create_goals_chart(goals)
        st.plotly_chart(fig, use_container_width=True)
        
        # Lista detalhada de metas
        for goal in goals:
            self._render_goal_card(goal)
    
    def _create_goals_chart(self, goals):
        """Cria gráfico de barras com o progresso das metas"""
        df = pd.DataFrame(goals)
        df['remaining'] = df['target_amount'] - df['current_amount']
        
        fig = go.Figure()
        
        # Barra do valor atual (atingido)
        fig.add_trace(go.Bar(
            name='Valor Atual',
            x=df['name'],
            y=df['current_amount'],
            marker_color='#00cc96',
            text=df['progress_percentage'].round(1).astype(str) + '%',
            textposition='auto',
        ))
        
        # Barra do valor restante
        fig.add_trace(go.Bar(
            name='Falta',
            x=df['name'],
            y=df['remaining'],
            marker_color='#ffa15a',
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Progresso das Metas",
            barmode='stack',
            xaxis_title="Metas",
            yaxis_title="Valor (R$)",
            showlegend=True,
            height=400
        )
        
        return fig
    
    def _render_goal_card(self, goal):
        """Renderiza um card de meta"""
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                # Barra de progresso
                progress = goal['progress_percentage'] / 100
                st.progress(progress)
                
                st.subheader(goal['name'])
                st.caption(f"🎯 Categoria: {goal['category']} | ⭐ Prioridade: {goal['priority']}")
                st.caption(f"📅 Vence em: {goal['deadline'].strftime('%d/%m/%Y')} ({goal['days_remaining']} dias restantes)")
            
            with col2:
                # Informações de valor
                st.write(f"**R$ {goal['current_amount']:,.2f}** de **R$ {goal['target_amount']:,.2f}**")
                st.write(f"**({goal['progress_percentage']:.1f}% concluído)**")
                
                # Calcular economia mensal necessária
                if goal['days_remaining'] > 0:
                    monthly_saving = goal['remaining_amount'] / (goal['days_remaining'] / 30)
                    st.caption(f"💡 Economize R$ {monthly_saving:,.2f} por mês")
            
            with col3:
                # Ações
                if st.button("✏️ Editar", key=f"edit_{goal['id']}", use_container_width=True):
                    st.session_state.editing_goal_id = goal['id']
                    st.rerun()
                
                if st.button("🗑️ Excluir", key=f"delete_{goal['id']}", use_container_width=True):
                    if goal_service.delete_goal(goal['id']):
                        st.success("✅ Meta excluída!")
                        st.rerun()
            
            st.markdown("---")
    
    def _show_edit_goal_form(self, goal_id):
        """Mostra formulário de edição de meta"""
        st.markdown('<div class="edit-form">', unsafe_allow_html=True)
        
        # Botão voltar
        if st.button("← Voltar para lista"):
            st.session_state.editing_goal_id = None
            st.rerun()
        
        st.subheader("✏️ Editar Meta")
        
        goal = goal_service.get_goal_by_id(goal_id)
        if not goal:
            st.error("Meta não encontrada")
            st.session_state.editing_goal_id = None
            st.rerun()
            return
        
        with st.form(f"edit_goal_form_{goal_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome da Meta", value=goal['name'])
                target_amount = st.number_input("Valor Alvo (R$)", min_value=0.01, step=100.0, value=float(goal['target_amount']))
                category = st.selectbox("Categoria", 
                                      ["Viagem", "Reserva Emergencial", "Investimento", 
                                       "Estudos", "Casa", "Carro", "Outros"],
                                      index=["Viagem", "Reserva Emergencial", "Investimento", 
                                           "Estudos", "Casa", "Carro", "Outros"].index(goal['category']) 
                                      if goal['category'] in ["Viagem", "Reserva Emergencial", "Investimento", "Estudos", "Casa", "Carro", "Outros"] else 6)
            
            with col2:
                deadline = st.date_input("Data Limite", value=goal['deadline'])
                priority = st.select_slider("Prioridade", options=[1, 2, 3, 4, 5], value=goal['priority'])
                current_amount = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0, value=float(goal['current_amount']))
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    # Atualizar progresso
                    if goal_service.update_goal_progress(goal_id, current_amount):
                        st.success("✅ Meta atualizada!")
                        st.session_state.editing_goal_id = None
                        st.rerun()
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.editing_goal_id = None
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Instância e execução
goals_page = GoalsPage()
goals_page.show_goals()