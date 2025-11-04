import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.alert_service import alert_service
from services.finance_calculator import FinanceCalculator

st.set_page_config(page_title="Alertas", page_icon="⚡", layout="wide")

class AlertsPage:
    def __init__(self):
        self.user_id = 1
        self.finance_calc = FinanceCalculator()
    
    def show_alerts(self):
        st.markdown('<h1 class="main-header">⚡ Alertas Inteligentes</h1>', unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="alerts_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="alerts_year")
        
        # Alertas em tempo real
        st.subheader("🔔 Alertas Atuais")
        
        alerts = alert_service.get_all_alerts(self.user_id, mes, ano)
        
        if not alerts:
            st.success("🎉 Tudo sob controle! Nenhum alerta no momento.")
        else:
            for alert in alerts:
                if alert['severity'] == 'high':
                    st.error(f"🚨 {alert['message']}")
                elif alert['severity'] == 'medium':
                    st.warning(f"⚠️ {alert['message']}")
                else:
                    st.info(f"💡 {alert['message']}")
        
        # Status diário detalhado
        st.subheader("📅 Controle Diário - Método Breno")
        
        daily_status = self.finance_calc.get_daily_budget_status(self.user_id, mes, ano)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Gasto Hoje", 
                f"R$ {daily_status['today_spent']:.2f}",
                delta=f"{daily_status['today_spent'] - daily_status['daily_budget']:.2f}" if daily_status['today_spent'] > daily_status['daily_budget'] else None,
                delta_color="inverse"
            )
        
        with col2:
            st.metric("🎯 Orçamento Diário", f"R$ {daily_status['daily_budget']:.2f}")
        
        with col3:
            st.metric("⏳ Dias Restantes", daily_status['remaining_days'])
        
        with col4:
            st.metric("📊 Saldo Mensal", f"R$ {daily_status['remaining_budget']:.2f}")
        
        # Recomendações inteligentes
        st.subheader("💡 Recomendações do Dia")
        
        if daily_status['today_spent'] > daily_status['daily_budget']:
            st.error(f"""
            **🚨 RECOMENDAÇÃO URGENTE:**
            - Você excedeu seu orçamento diário em **R$ {daily_status['today_spent'] - daily_status['daily_budget']:.2f}**
            - **EVITE GASTOS NÃO ESSENCIAIS** pelo resto do dia
            - Considere adiar compras não urgentes para amanhã
            """)
        elif daily_status['today_spent'] > daily_status['daily_budget'] * 0.8:
            st.warning(f"""
            **⚠️ ATENÇÃO:**
            - Você já utilizou **{((daily_status['today_spent'] / daily_status['daily_budget']) * 100):.1f}%** do seu orçamento diário
            - **REDUZA GASTOS** pelo resto do dia
            - Orçamento restante: **R$ {daily_status['daily_budget'] - daily_status['today_spent']:.2f}**
            """)
        else:
            st.success(f"""
            **🎉 VOCÊ ESTÁ NO CONTROLE!**
            - Ainda pode gastar **R$ {daily_status['daily_budget'] - daily_status['today_spent']:.2f}** hoje
            - **{((daily_status['today_spent'] / daily_status['daily_budget']) * 100):.1f}%** do orçamento utilizado
            - Mantenha esse excelente trabalho!
            """)
        
        # Previsão para o mês
        st.subheader("📈 Projeção do Mês")
        
        if daily_status['remaining_days'] > 0:
            daily_average = daily_status['remaining_budget'] / daily_status['remaining_days']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Para atingir sua meta:**
                - Gaste até **R$ {daily_average:.2f} por dia**
                - Ou **R$ {daily_average * 7:.2f} por semana**
                - Dias restantes: **{daily_status['remaining_days']}**
                """)
            
            with col2:
                if daily_average < daily_status['daily_budget']:
                    st.success("**🎉 Você está à frente do planejado!**")
                else:
                    st.warning("**📊 Atenção: precisa economizar um pouco**")

# Instância e execução
alerts_page = AlertsPage()
alerts_page.show_alerts()