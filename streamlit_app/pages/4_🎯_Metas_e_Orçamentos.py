import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from services.goal_service import goal_service
from services.budget_service import budget_service
from services.ai_processor import ai_processor
from utils import check_authentication, month_year_filter

st.set_page_config(page_title="Metas e Orçamentos", page_icon="🎯", layout="wide")

telegram_id = check_authentication()
st.markdown('<h1 class="main-header">🎯 Metas e Orçamentos</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎯 Metas Financeiras", "💰 Orçamentos por Categoria"])

with tab1:
    st.subheader("Gerencie suas Metas de Longo Prazo")
    with st.expander("➕ Adicionar Nova Meta"):
        with st.form("new_goal_form"):
            name = st.text_input("Nome da Meta*")
            target = st.number_input("Valor Alvo (R$)*", min_value=0.01, value=1000.0)
            deadline = st.date_input("Data Limite*", value=date.today() + timedelta(days=365))
            priority = st.select_slider("Prioridade", options=[1, 2, 3, 4, 5], value=3)
            if st.form_submit_button("🎯 Criar Meta"):
                if name and target > 0:
                    goal_service.create_goal(telegram_id, name, target, deadline.strftime('%Y-%m-%d'), priority=priority)
                    st.success("✅ Meta criada!"); st.rerun()
                else: st.error("Preencha os campos obrigatórios.")
    
    goals = goal_service.get_user_goals(telegram_id)
    if goals:
        df_goals = pd.DataFrame(goals)
        fig = go.Figure(data=[go.Bar(name='Atual', x=df_goals['name'], y=df_goals['current_amount'], marker_color='#00cc96'),
                             go.Bar(name='Falta', x=df_goals['name'], y=df_goals['target_amount'] - df_goals['current_amount'], marker_color='#ffa15a')])
        fig.update_layout(barmode='stack', title='Progresso das Metas')
        st.plotly_chart(fig, width='stretch')
    else: st.info("Você ainda não tem metas definidas.")

with tab2:
    st.subheader("Defina Limites de Gasto Mensais")
    month, year = month_year_filter("budget")
    with st.expander("🎯 Definir Novo Orçamento"):
        with st.form("new_budget_form"):
            category = st.selectbox("Categoria", list(ai_processor.categories.keys()))
            amount = st.number_input("Limite Mensal (R$)", min_value=1.0, value=500.0)
            if st.form_submit_button("💾 Salvar Orçamento"):
                if budget_service.set_budget(telegram_id, category, amount, month, year):
                    st.success("✅ Orçamento salvo!"); st.rerun()
    
    budget_data = budget_service.get_budgets_with_status(telegram_id, month, year)
    if budget_data['budgets']:
        df_budget = pd.DataFrame(budget_data['budgets'])
        fig = go.Figure(data=[go.Bar(name='Orçado', x=df_budget['category'], y=df_budget['monthly_limit'], marker_color='#636efa'),
                             go.Bar(name='Gasto', x=df_budget['category'], y=df_budget['spent'], marker_color='#ef553b')])
        fig.update_layout(barmode='group', title='Orçado vs Gasto Real')
        st.plotly_chart(fig, width='stretch')
    else: st.info("Defina seu primeiro orçamento acima!")