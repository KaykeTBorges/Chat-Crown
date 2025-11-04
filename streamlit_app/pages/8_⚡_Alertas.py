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
        self.user_id = st.session_state.user_id
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
                if alert.get('severity') == 'high':
                    st.error(f"🚨 {alert.get('message', '')}")
                elif alert.get('severity') == 'medium':
                    st.warning(f"⚠️ {alert.get('message', '')}")
                else:
                    st.info(f"💡 {alert.get('message', '')}")
        
        # ✅ CORREÇÃO: Status diário com tratamento de erro
        st.subheader("📅 Controle Diário - Método Breno")
        
        try:
            daily_status = self.finance_calc.get_daily_budget_status(self.user_id, mes, ano)
            
            if not daily_status or 'situacao_dias' not in daily_status:
                st.info("📊 Nenhum dado disponível para controle diário.")
                return
            
            # Encontrar dados do dia atual
            dia_atual = None
            for dia in daily_status['situacao_dias']:
                if dia.get('status') == 'hoje' or 'HOJE' in str(dia.get('data', '')):
                    dia_atual = dia
                    break
            
            if dia_atual:
                today_spent = dia_atual.get('gasto', 0)
                daily_budget = dia_atual.get('meta_diaria', 0)
                remaining_days = daily_status.get('dias_restantes', 0)
                remaining_budget = daily_status.get('saldo_restante_mes', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_value = today_spent - daily_budget if today_spent > daily_budget else None
                    st.metric(
                        "💰 Gasto Hoje", 
                        f"R$ {today_spent:.2f}",
                        delta=f"{delta_value:.2f}" if delta_value else None,
                        delta_color="inverse" if delta_value else "off"
                    )
                
                with col2:
                    st.metric("🎯 Orçamento Diário", f"R$ {daily_budget:.2f}")
                
                with col3:
                    st.metric("⏳ Dias Restantes", remaining_days)
                
                with col4:
                    st.metric("📊 Saldo Mensal", f"R$ {remaining_budget:.2f}")
                
                # Recomendações inteligentes
                st.subheader("💡 Recomendações do Dia")
                
                if today_spent > daily_budget:
                    st.error(f"""
                    **🚨 RECOMENDAÇÃO URGENTE:**
                    - Você excedeu seu orçamento diário em **R$ {today_spent - daily_budget:.2f}**
                    - **EVITE GASTOS NÃO ESSENCIAIS** pelo resto do dia
                    - Considere adiar compras não urgentes para amanhã
                    """)
                elif today_spent > daily_budget * 0.8:
                    st.warning(f"""
                    **⚠️ ATENÇÃO:**
                    - Você já utilizou **{((today_spent / daily_budget) * 100):.1f}%** do seu orçamento diário
                    - **REDUZA GASTOS** pelo resto do dia
                    - Orçamento restante: **R$ {daily_budget - today_spent:.2f}**
                    """)
                else:
                    st.success(f"""
                    **🎉 VOCÊ ESTÁ NO CONTROLE!**
                    - Ainda pode gastar **R$ {daily_budget - today_spent:.2f}** hoje
                    - **{((today_spent / daily_budget) * 100):.1f}%** do orçamento utilizado
                    - Mantenha esse excelente trabalho!
                    """)
                
                # Previsão para o mês
                if remaining_days > 0:
                    st.subheader("📈 Projeção do Mês")
                    daily_average = remaining_budget / remaining_days
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Para atingir sua meta:**
                        - Gaste até **R$ {daily_average:.2f} por dia**
                        - Ou **R$ {daily_average * 7:.2f} por semana**
                        - Dias restantes: **{remaining_days}**
                        """)
                    
                    with col2:
                        if daily_average < daily_budget:
                            st.success("**🎉 Você está à frente do planejado!**")
                        else:
                            st.warning("**📊 Atenção: precisa economizar um pouco**")
            else:
                st.info("📅 Nenhum dado disponível para o dia atual.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados diários: {str(e)}")
            st.info("📝 Adicione algumas transações para ver o controle diário.")

# Instância e execução
alerts_page = AlertsPage()
alerts_page.show_alerts()