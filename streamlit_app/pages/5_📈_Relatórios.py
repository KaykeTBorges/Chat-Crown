import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.transactions_service import transactions_service
from utils import check_authentication, month_year_filter

st.set_page_config(page_title="Relatórios", page_icon="📈", layout="wide")

# Authentication and month/year filter used for the reports.
telegram_id = check_authentication()
month, year = month_year_filter("reports")

st.markdown('<h1 class="main-header">📈 Relatórios Detalhados</h1>', unsafe_allow_html=True)

# Get transactions for the current month using the existing service filters.
# Ideally, the service would expose a dedicated method for this use case.
filters = {"date_range": "current_month", "sort_by": "date_asc"}
if month != datetime.now().month or year != datetime.now().year:
    # Custom logic for loading historical data would be needed here.
    st.info("Relatórios personalizados para outros meses ainda não implementados. Mostrando o mês atual.")
    
transactions, _ = transactions_service.get_transactions(telegram_id=telegram_id, filters=filters)

if not transactions:
    st.warning("Nenhuma transação para gerar relatórios.")
    st.stop()

st.subheader("📊 Análise por Categoria")
df = pd.DataFrame([{'Categoria': t.category, 'Tipo': t.type, 'Valor': t.amount} for t in transactions])
category_summary = df.groupby(['Categoria', 'Tipo']).sum().reset_index()
st.dataframe(category_summary.pivot(index='Categoria', columns='Tipo', values='Valor').fillna(0).style.format("{:.2f}"))

st.subheader("🥧 Distribuição por Categoria")
total_by_cat = df.groupby('Categoria')['Valor'].sum().reset_index()
if not total_by_cat.empty:
    fig = px.pie(total_by_cat, values='Valor', names='Categoria', title=f"Distribuição por Categoria - {month:02d}/{year}")
    st.plotly_chart(fig, width='stretch')

st.subheader("🔍 Análise por Tipo de Transação")
type_summary = df.groupby('Tipo')['Valor'].sum().reset_index()
fig_type = px.bar(type_summary, x='Tipo', y='Valor', title="Total por Tipo", color='Tipo')
st.plotly_chart(fig_type, width='stretch')