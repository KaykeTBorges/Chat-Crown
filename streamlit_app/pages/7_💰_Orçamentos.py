import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.budget_service import budget_service
from services.database import db_manager
from services.ai_processor import ai_processor

st.set_page_config(page_title="Orçamentos", page_icon="💰", layout="wide")

class BudgetPage:
    def __init__(self):
        self.user_id = st.session_state.user_id
    
    def show_budgets(self):
        st.markdown('<h1 class="main-header">💰 Orçamentos por Categoria</h1>', unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="budget_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="budget_year")
        
        # Carregar dados
        budget_data = budget_service.get_budgets_with_status(self.user_id, mes, ano)
        
        # Alertas em destaque
        if budget_data['alerts']:
            st.subheader("🔔 Alertas de Orçamento")
            for alert in budget_data['alerts']:
                if "🚨" in alert:
                    st.error(alert)
                else:
                    st.warning(alert)
        
        # Adicionar/Editar orçamento
        with st.expander("🎯 Definir Novo Orçamento", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                category = st.selectbox("Categoria", list(ai_processor.categories.keys()))
            
            with col2:
                amount = st.number_input("Limite Mensal (R$)", min_value=1.0, value=500.0, step=50.0)
            
            with col3:
                st.write("")  # Espaço
                if st.button("💾 Salvar Orçamento", use_container_width=True):
                    if budget_service.set_budget(self.user_id, category, amount, mes, ano):
                        st.success("✅ Orçamento salvo!")
                        st.rerun()
        
        # Visualização dos orçamentos
        if budget_data['budgets']:
            # Métricas gerais
            total_limit = sum(b['monthly_limit'] for b in budget_data['budgets'])
            total_spent = sum(b['spent'] for b in budget_data['budgets'])
            total_remaining = total_limit - total_spent
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orçado", f"R$ {total_limit:,.2f}")
            with col2:
                st.metric("Total Gasto", f"R$ {total_spent:,.2f}")
            with col3:
                st.metric("Saldo Restante", f"R$ {total_remaining:,.2f}")
            
            # Gráfico
            st.subheader("📊 Orçado vs Gasto Real")
            df = pd.DataFrame(budget_data['budgets'])
            fig = px.bar(df, x='category', y=['monthly_limit', 'spent'],
                        title="Comparação: Orçado vs Gasto Real",
                        barmode='group',
                        labels={'value': 'Valor (R$)', 'category': 'Categoria', 'variable': 'Tipo'})
            fig.update_traces(hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}')
            st.plotly_chart(fig, use_container_width=True)
            
            # Lista detalhada
            st.subheader("📋 Detalhes por Categoria")
            
            for budget in budget_data['budgets']:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    # Barra de progresso colorida
                    progress = budget['usage_percentage'] / 100
                    color = "🔴" if budget['alert_level'] == 'exceeded' else "🟡" if budget['alert_level'] == 'warning' else "🟢"
                    
                    st.progress(progress)
                    st.write(f"**{color} {budget['category']}**")
                    st.caption(f"{budget['usage_percentage']:.1f}% utilizado")
                
                with col2:
                    st.metric("Gasto", f"R$ {budget['spent']:,.2f}")
                
                with col3:
                    st.metric("Limite", f"R$ {budget['monthly_limit']:,.2f}")
                
                with col4:
                    remaining = budget['remaining']
                    if budget['alert_level'] == 'exceeded':
                        st.error(f"R$ {remaining:,.2f}")
                    elif budget['alert_level'] == 'warning':
                        st.warning(f"R$ {remaining:,.2f}")
                    else:
                        st.success(f"R$ {remaining:,.2f}")
                    st.caption("Restante")
                
                st.markdown("---")
        else:
            st.info("💡 Defina seu primeiro orçamento acima para começar!")

# Instância e execução
budget_page = BudgetPage()
budget_page.show_budgets()