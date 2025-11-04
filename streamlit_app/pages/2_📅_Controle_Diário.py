# pages/2_📅_Controle_Diário.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.finance_calculator import finance_calculator


st.set_page_config(page_title="Controle Diário", page_icon="📅", layout="wide")


class DailyControlPage:
    def __init__(self):
        self.user_id = st.session_state.user_id

    def show_daily_control(self):
        st.markdown('<h1 class="main-header">📅 Controle Diário Inteligente</h1>', unsafe_allow_html=True)

        # ---------------------- Filtros ----------------------
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="daily_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="daily_year")

        # ---------------------- Obter status diário ----------------------
        status_diario = finance_calculator.get_daily_budget_status(self.user_id, mes, ano)

        if not status_diario['situacao_dias']:
            st.info("📝 Nenhum dado disponível para controle diário.")
            return

        # ---------------------- Cartão do dia atual ----------------------
        dia_atual = status_diario.get('dia_atual')
        if dia_atual:
            self._show_current_day_card(dia_atual)

        # ---------------------- Métricas rápidas ----------------------
        self._show_quick_metrics(status_diario)

        # ---------------------- Tabela de controle diário ----------------------
        st.subheader("📋 Controle Dia a Dia")
        self._show_daily_table(status_diario['situacao_dias'])

        # ---------------------- Gráfico de evolução diária ----------------------
        st.subheader("📈 Evolução do Saldo Diário")
        self._show_daily_evolution_chart(status_diario['situacao_dias'])

    # ---------------------- Helpers ----------------------
    def _show_current_day_card(self, dia_atual):
        saldo_acumulado = dia_atual['saldo_acumulado'] - dia_atual['meta_diaria']
        orcamento_hoje = dia_atual['meta_diaria'] + max(0, saldo_acumulado)

        if dia_atual['gasto'] > orcamento_hoje:
            cor, status, cor_borda = "🔴", "ULTRAPASSADO", "border-left: 5px solid #ef553b;"
        elif dia_atual['gasto'] > dia_atual['meta_diaria']:
            cor, status, cor_borda = "🟡", "ATENÇÃO", "border-left: 5px solid #ffa15a;"
        else:
            cor, status, cor_borda = "🟢", "DENTRO DO ORÇAMENTO", "border-left: 5px solid #00cc96;"

        st.markdown(f"""
        <div style="{cor_borda} background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h3 style="margin: 0; color: #333;">{cor} HOJE - {dia_atual['data']}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <strong>💰 Gasto Hoje:</strong><br>
                    <span style="font-size: 1.5rem; color: {'#ef553b' if dia_atual['gasto'] > orcamento_hoje else '#333'}">
                        R$ {dia_atual['gasto']:,.2f}
                    </span>
                </div>
                <div>
                    <strong>🎯 Orçamento Disponível:</strong><br>
                    <span style="font-size: 1.5rem; color: #00cc96">
                        R$ {orcamento_hoje:,.2f}
                    </span>
                </div>
                <div>
                    <strong>📊 Status:</strong><br>
                    <span style="font-size: 1.2rem; font-weight: bold; color: {'#ef553b' if dia_atual['gasto'] > orcamento_hoje else '#ffa15a' if dia_atual['gasto'] > dia_atual['meta_diaria'] else '#00cc96'}">
                        {status}
                    </span>
                </div>
            </div>
            {f"<div style='margin-top: 1rem; color: #666;'><strong>💡 Saldo Acumulado:</strong> R$ {saldo_acumulado:,.2f} dos dias anteriores</div>" if saldo_acumulado > 0 else ""}
        </div>
        """, unsafe_allow_html=True)

    def _show_quick_metrics(self, status_diario):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "💰 Gasto Variável Mês",
                f"R$ {status_diario['total_gasto_variavel_mes']:,.2f}",
                delta_color="inverse"
            )
        with col2:
            st.metric(
                "🎯 Saldo Restante",
                f"R$ {status_diario['saldo_restante_mes']:,.2f}",
                delta_color="normal" if status_diario['saldo_restante_mes'] >= 0 else "off"
            )
        with col3:
            st.metric(
                "📊 Média Ajustada",
                f"R$ {status_diario['media_ajustada_restante']:,.2f}",
                help="Média diária considerando gastos já realizados"
            )
        with col4:
            st.metric(
                "⏳ Dias Restantes",
                status_diario['dias_restantes']
            )

    def _show_daily_table(self, situacao_dias):
        dados = []
        for dia in situacao_dias:
            saldo_anterior = dia['saldo_acumulado'] - dia['meta_diaria'] + dia['gasto']
            orcamento_disponivel = dia['meta_diaria'] + max(0, saldo_anterior)
            dados.append({
                'Dia': dia['data'],
                'Meta Diária': f"R$ {dia['meta_diaria']:,.2f}",
                'Gasto Real': f"R$ {dia['gasto']:,.2f}",
                'Orçamento Disponível': f"R$ {orcamento_disponivel:,.2f}",
                'Saldo Acumulado': f"R$ {dia['saldo_acumulado']:,.2f}",
                'Status': self._get_daily_status_emoji(dia, orcamento_disponivel)
            })

        df = pd.DataFrame(dados)

        def color_current_day(row):
            if 'HOJE' in row['Status']:
                return ['background-color: #e8f5e8'] * len(row)
            elif '🔴' in row['Status']:
                return ['background-color: #ffeaea'] * len(row)
            elif '🟡' in row['Status']:
                return ['background-color: #fff4e6'] * len(row)
            else:
                return [''] * len(row)

        st.dataframe(df.style.apply(color_current_day, axis=1), use_container_width=True, height=400)

    def _get_daily_status_emoji(self, dia, orcamento_disponivel):
        if dia['status'] == 'futuro':
            return "⏳"
        elif dia['gasto'] > orcamento_disponivel:
            return "🔴 Ultrapassado"
        elif dia['gasto'] > dia['meta_diaria']:
            return "🟡 Atenção"
        elif dia['gasto'] > 0:
            return "🟢 Dentro"
        else:
            return "💤 Não gastou"

    def _show_daily_evolution_chart(self, situacao_dias):
        dias = [dia['data'] for dia in situacao_dias]
        saldos = [dia['saldo_acumulado'] for dia in situacao_dias]
        gastos = [dia['gasto'] for dia in situacao_dias]
        metas = [dia['meta_diaria'] for dia in situacao_dias]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dias, y=saldos, mode='lines+markers', name='Saldo Acumulado',
                                 line=dict(color='#636efa', width=3), marker=dict(size=6)))
        fig.add_trace(go.Bar(x=dias, y=gastos, name='Gasto Real', marker_color='#ef553b', opacity=0.7))
        fig.add_trace(go.Scatter(x=dias, y=metas, mode='lines', name='Meta Diária',
                                 line=dict(color='#00cc96', width=2, dash='dash')))

        fig.update_layout(
            title="Evolução do Saldo Diário Acumulado",
            xaxis_title="Dia do Mês",
            yaxis_title="Valor (R$)",
            showlegend=True,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)


# ---------------------- Instância e execução ----------------------
daily_page = DailyControlPage()
daily_page.show_daily_control()
