import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.database import db_manager
from services.finance_calculator import finance_calculator

st.set_page_config(page_title="Relatórios", page_icon="📈", layout="wide")

class ReportsPage:
    def __init__(self):
        self.user_id = 1
    
    def show_reports(self):
        st.markdown('<h1 class="main-header">📈 Relatórios Detalhados</h1>', unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="reports_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="reports_year")
        
        transacoes = self._get_monthly_transactions(mes, ano)
        
        if not transacoes:
            st.warning("Nenhuma transação para gerar relatórios.")
            return
        
        # Análise por categoria
        st.subheader("📊 Análise por Categoria")
        
        # Agrupar por categoria e tipo
        dados_categoria = {}
        for transacao in transacoes:
            if transacao.category not in dados_categoria:
                dados_categoria[transacao.category] = {
                    'renda': 0, 'despesa_fixa': 0, 'despesa_variavel': 0, 'economia': 0
                }
            dados_categoria[transacao.category][transacao.type] += transacao.amount
        
        # Criar DataFrame para análise
        analise_data = []
        for categoria, valores in dados_categoria.items():
            total = sum(valores.values())
            analise_data.append({
                'Categoria': categoria,
                'Renda': valores['renda'],
                'Despesa Fixa': valores['despesa_fixa'],
                'Despesa Variável': valores['despesa_variavel'],
                'Economia': valores['economia'],
                'Total': total
            })
        
        df_analise = pd.DataFrame(analise_data)
        st.dataframe(df_analise, use_container_width=True)
        
        # Gráfico de pizza por categoria
        st.subheader("🥧 Distribuição por Categoria")
        
        totais_por_categoria = []
        for categoria, valores in dados_categoria.items():
            total_categoria = sum(valores.values())
            if total_categoria > 0:
                totais_por_categoria.append({
                    'Categoria': categoria,
                    'Total': total_categoria
                })
        
        if totais_por_categoria:
            df_pizza = pd.DataFrame(totais_por_categoria)
            fig = px.pie(df_pizza, values='Total', names='Categoria', 
                        title=f"Distribuição de Gastos por Categoria - {mes:02d}/{ano}")
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de tendências (últimos 3 meses)
        st.subheader("📈 Tendência dos Últimos 3 Meses")
        self._show_trends_chart()
        
        # Análise de tipos
        st.subheader("🔍 Análise por Tipo de Transação")
        
        totais_por_tipo = {
            'Renda': 0,
            'Despesa Fixa': 0,
            'Despesa Variável': 0,
            'Economia': 0
        }
        
        for transacao in transacoes:
            if transacao.type == 'renda':
                totais_por_tipo['Renda'] += transacao.amount
            elif transacao.type == 'despesa_fixa':
                totais_por_tipo['Despesa Fixa'] += transacao.amount
            elif transacao.type == 'despesa_variavel':
                totais_por_tipo['Despesa Variável'] += transacao.amount
            elif transacao.type == 'economia':
                totais_por_tipo['Economia'] += transacao.amount
        
        df_tipo = pd.DataFrame([
            {'Tipo': 'Renda', 'Valor': totais_por_tipo['Renda']},
            {'Tipo': 'Despesa Fixa', 'Valor': totais_por_tipo['Despesa Fixa']},
            {'Tipo': 'Despesa Variável', 'Valor': totais_por_tipo['Despesa Variável']},
            {'Tipo': 'Economia', 'Valor': totais_por_tipo['Economia']}
        ])
        
        fig_tipo = px.bar(df_tipo, x='Tipo', y='Valor', 
                         title="Distribuição por Tipo de Transação",
                         color='Tipo',
                         color_discrete_map={
                             'Renda': '#00cc96',
                             'Despesa Fixa': '#ef553b',
                             'Despesa Variável': '#ffa15a',
                             'Economia': '#636efa'
                         })
        st.plotly_chart(fig_tipo, use_container_width=True)
    
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
    
    def _show_trends_chart(self):
        """Mostra gráfico de tendências"""
        meses_data = []
        
        # Coletar dados dos últimos 3 meses
        for i in range(3):
            data_ref = datetime.now() - timedelta(days=30*i)
            mes = data_ref.month
            ano = data_ref.year
            
            resumo = finance_calculator.get_monthly_summary(self.user_id, mes, ano)
            if resumo['transacoes_count'] > 0:
                meses_data.append({
                    'Período': f"{mes:02d}/{ano}",
                    'Renda': resumo['total_renda'],
                    'Despesas': resumo['total_despesas'],
                    'Economia': resumo['total_economia']
                })
        
        if meses_data:
            df_tendencia = pd.DataFrame(meses_data)
            fig = px.line(df_tendencia, x='Período', y=['Renda', 'Despesas', 'Economia'],
                         title="Evolução Financeira - Últimos 3 Meses",
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise de tendências.")

# Instância e execução
reports_page = ReportsPage()
reports_page.show_reports()