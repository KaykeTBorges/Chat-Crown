import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from services.alert_service import alert_service

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.database import db_manager
from services.finance_calculator import finance_calculator

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

class DashboardPage:
    def __init__(self):
        self.user_id = 1
    
    def show_dashboard(self):
        st.markdown('<h1 class="main-header">📊 Dashboard Financeiro</h1>', unsafe_allow_html=True)

         # 🔔 NOVO: ALERTAS EM DESTAQUE
        st.subheader("🔔 Alertas do Sistema")
        alerts = alert_service.get_all_alerts(self.user_id, mes, ano)
        
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'high':
                    st.error(f"🚨 {alert['message']}")
                elif alert['severity'] == 'medium':
                    st.warning(f"⚠️ {alert['message']}")
                else:
                    st.info(f"💡 {alert['message']}")
        else:
            st.success("🎉 Tudo sob controle! Nenhum alerta no momento.")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="dashboard_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="dashboard_year")
        
        # Resumo do mês
        resumo = finance_calculator.get_monthly_summary(self.user_id, mes, ano)
        
        if resumo['transacoes_count'] == 0:
            st.warning("📝 Nenhuma transação registrada para este período.")
            st.info("💡 Use o Telegram bot para registrar suas primeiras transações!")
            return
        
        # Métricas principais
        st.subheader("📈 Métricas do Mês")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Renda Total", 
                f"R$ {resumo['total_renda']:,.2f}",
                delta=f"{resumo['total_renda']/resumo['total_renda']*100:.1f}%" if resumo['total_renda'] > 0 else None
            )
        
        with col2:
            st.metric(
                "💸 Despesas Totais", 
                f"R$ {resumo['total_despesas']:,.2f}",
                delta=f"-{(resumo['total_despesas']/resumo['total_renda']*100):.1f}%" if resumo['total_renda'] > 0 else None,
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "🚀 Economia Real", 
                f"R$ {resumo['total_economia']:,.2f}",
                delta=f"{(resumo['economia_real_vs_meta']):,.2f} vs Meta"
            )
        
        with col4:
            cor_saldo = "normal" if resumo['saldo_final'] >= 0 else "off"
            st.metric(
                "⚖️ Saldo Final", 
                f"R$ {resumo['saldo_final']:,.2f}",
                delta_color=cor_saldo
            )
        
        # Gráfico de distribuição
        st.subheader("📊 Distribuição Financeira")
        self._show_distribution_chart(resumo)
        
        # Alertas
        if resumo['alertas']:
            st.subheader("⚠️ Alertas do Sistema")
            for alerta in resumo['alertas']:
                st.markdown(f'<div class="alert-box">{alerta}</div>', unsafe_allow_html=True)
    
    def _show_distribution_chart(self, resumo):
        categorias = ['Renda', 'Despesas Fixas', 'Despesas Variáveis', 'Economia']
        valores = [
            resumo['total_renda'],
            resumo['total_despesas_fixas'],
            resumo['total_despesas_variaveis'],
            resumo['total_economia']
        ]
        cores = ['#00cc96', '#ef553b', '#ffa15a', '#636efa']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categorias, 
                y=valores,
                marker_color=cores,
                text=[f'R$ {v:,.2f}' for v in valores],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Distribuição Financeira Mensal",
            xaxis_title="Categorias",
            yaxis_title="Valor (R$)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Instância e execução
dashboard_page = DashboardPage()
dashboard_page.show_dashboard()