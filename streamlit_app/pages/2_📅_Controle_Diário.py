import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.finance_calculator import finance_calculator
from utils import check_authentication, month_year_filter

st.set_page_config(page_title="Controle Diário", page_icon="📅", layout="wide")

# Authentication and month/year selection for this daily view.
telegram_id = check_authentication()
month, year = month_year_filter("daily")

st.markdown('<h1 class="main-header">📅 Controle Diário (Método Breno)</h1>', unsafe_allow_html=True)

with st.expander("💡 Entenda o Método Breno Nogueira"):
    st.info("""- **Economia de 25%**: Guarde pelo menos 25% da sua renda.\n- **Despesas Fixas Controladas**.\n- **Gastos Variáveis Conscientes**: O que sobra é seu limite diário.""")

status_diario = finance_calculator.get_daily_budget_status(telegram_id, month, year)

if not status_diario or not status_diario.get('situacao_dias'):
    st.warning("Nenhum dado disponível para controle diário.")
    st.stop()

# --- Contextual alerts for the current day ---
st.subheader("🔔 Recomendações do Dia")
dia_atual = next((d for d in status_diario['situacao_dias'] if d.get('status') == 'hoje'), None)

if dia_atual:
    today_spent = dia_atual.get('gasto', 0)
    daily_budget = dia_atual.get('meta_diaria', 0)
    
    if today_spent > daily_budget:
        st.error(f"**🚨 RECOMENDAÇÃO URGENTE:**\n- Você excedeu seu orçamento diário em **R$ {today_spent - daily_budget:.2f}**\n- **EVITE GASTOS NÃO ESSENCIAIS** pelo resto do dia.")
    elif today_spent > daily_budget * 0.8:
        st.warning(f"**⚠️ ATENÇÃO:**\n- Você já utilizou **{((today_spent / daily_budget) * 100):.1f}%** do seu orçamento diário.\n- Orçamento restante: **R$ {daily_budget - today_spent:.2f}**.")
    else:
        st.success(f"**🎉 VOCÊ ESTÁ NO CONTROLE!**\n- Ainda pode gastar **R$ {daily_budget - today_spent:.2f}** hoje.")
else:
    st.info("📅 Nenhum dado disponível para o dia atual.")

st.markdown("---")

# --- Monthly overview metrics and charts ---
st.subheader("📊 Resumo do Mês")
col1, col2, col3 = st.columns(3)
col1.metric("Gasto Variável", f"R$ {status_diario['total_gasto_variavel_mes']:,.2f}")
col2.metric("Saldo Restante", f"R$ {status_diario['saldo_restante_mes']:,.2f}")
col3.metric("Média Diária Restante", f"R$ {status_diario['media_ajustada_restante']:,.2f}")

st.subheader("📈 Evolução do Saldo Diário")
situacao_dias = status_diario['situacao_dias']
fig = go.Figure()
fig.add_trace(go.Scatter(x=[d['data'] for d in situacao_dias], y=[d['saldo_acumulado'] for d in situacao_dias], mode='lines+markers', name='Saldo Acumulado'))
fig.update_layout(title="Evolução do Saldo Acumulado", xaxis_title="Dia", yaxis_title="Valor (R$)")
st.plotly_chart(fig, width='stretch')

st.subheader("📋 Controle Dia a Dia")
df_daily = pd.DataFrame(situacao_dias)
st.dataframe(df_daily[['data', 'gasto', 'meta_diaria', 'saldo_acumulado']].rename(columns={'data': 'Data', 'gasto': 'Gasto', 'meta_diaria': 'Meta Diária', 'saldo_acumulado': 'Saldo Acumulado'}), use_container_width=True)