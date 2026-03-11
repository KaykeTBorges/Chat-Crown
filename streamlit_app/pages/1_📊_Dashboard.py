import streamlit as st
import plotly.graph_objects as go
from services.finance_calculator import finance_calculator
from services.alert_service import alert_service 
from utils import check_authentication, month_year_filter

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Authentication and time filter for this page.
telegram_id = check_authentication()
month, year = month_year_filter("dashboard")

st.markdown('<h1 class="main-header">📊 Dashboard Financeiro</h1>', unsafe_allow_html=True)

# --- System alerts section ---
st.subheader("🔔 Alertas do Sistema")
try:
    # This part depends on `alert_service.get_all_alerts()`.
    # If the service is not configured, the NameError is handled below.
    alerts = alert_service.get_all_alerts(telegram_id, month, year)
    if alerts:
        for alert in alerts:
            if alert.get('severity') == 'high':
                st.error(f"🚨 {alert.get('message', '')}")
            elif alert.get('severity') == 'medium':
                st.warning(f"⚠️ {alert.get('message', '')}")
            else:
                st.info(f"💡 {alert.get('message', '')}")
    else:
        st.success("🎉 Tudo sob controle! Nenhum alerta no momento.")
except NameError:
    st.info("Serviço de alertas não configurado.")
except Exception as e:
    st.error(f"Não foi possível carregar os alertas: {e}")

st.markdown("---")

# --- Main monthly summary logic ---
resumo = finance_calculator.get_monthly_summary(telegram_id, month, year)

if resumo['transacoes_count'] == 0:
    st.warning("📝 Nenhuma transação registrada para este período.")
    st.info("💡 Use o bot do Telegram para registrar suas primeiras transações!")
    st.stop()

st.subheader("📈 Métricas do Mês")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Renda Total", f"R$ {resumo['total_renda']:,.2f}")
col2.metric("💸 Despesas Totais", f"R$ {resumo['total_despesas']:,.2f}")
col3.metric("🚀 Economia Real", f"R$ {resumo['total_economia']:,.2f}")
col4.metric("⚖️ Saldo Final", f"R$ {resumo['saldo_final']:,.2f}")

st.subheader("📊 Distribuição Financeira")
fig = go.Figure(data=[
    go.Bar(name='Renda', x=['Renda'], y=[resumo['total_renda']], marker_color='#00cc96'),
    go.Bar(name='Despesas Fixas', x=['Despesas'], y=[resumo['total_despesas_fixas']], marker_color='#ef553b'),
    go.Bar(name='Despesas Variáveis', x=['Despesas'], y=[resumo['total_despesas_variaveis']], marker_color='#ffa15a'),
    go.Bar(name='Economia', x=['Economia'], y=[resumo['total_economia']], marker_color='#636efa')
])
fig.update_layout(barmode='stack', title_text='Distribuição Financeira Mensal')
st.plotly_chart(fig, width='stretch')