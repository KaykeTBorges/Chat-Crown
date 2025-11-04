# pages/6_🎯_Método_Breno.py
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.finance_calculator import finance_calculator

st.set_page_config(page_title="Método Breno", page_icon="🎯", layout="wide")


class BrenoMethodPage:
    def __init__(self):
        self.user_id = st.session_state.user_id

    def show_breno_method(self):
        st.markdown('<h1 class="main-header">🎯 Método Breno Nogueira</h1>', unsafe_allow_html=True)

        # ---------------------- Filtros ----------------------
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mês", range(1, 13), datetime.now().month - 1, key="breno_month")
        with col2:
            ano = st.selectbox("Ano", range(2020, 2031), datetime.now().year - 2020, key="breno_year")

        # ---------------------- Resumo do mês ----------------------
        resumo = finance_calculator.get_monthly_summary(self.user_id, mes, ano)

        if resumo['transacoes_count'] == 0:
            st.warning("Nenhum dado disponível para análise.")
            return

        # ---------------------- Explicação do método ----------------------
        st.info("""
        **💡 Sobre o Método Breno Nogueira:**
        - **Economia de 25%**: Guarde pelo menos 25% da sua renda
        - **Despesas Fixas Controladas**: Mantenha as despesas fixas sob controle
        - **Gastos Variáveis Conscientes**: Use o saldo disponível para gastos do dia a dia
        """)

        # ---------------------- Métricas do método ----------------------
        self._show_metrics(resumo)

        # ---------------------- Gráfico de progresso ----------------------
        self._show_breno_progress(resumo)

        # ---------------------- Detalhes adicionais ----------------------
        self._show_details(resumo)

    # ---------------------- Helpers ----------------------
    def _show_metrics(self, resumo):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🎯 Meta de Economia (25%)",
                f"R$ {resumo['meta_economia']:,.2f}",
                delta=f"R$ {resumo['economia_real_vs_meta']:,.2f}",
                delta_color="normal" if resumo['economia_real_vs_meta'] >= 0 else "off"
            )
        with col2:
            st.metric(
                "💼 Saldo Disponível",
                f"R$ {resumo['saldo_disponivel']:,.2f}",
                delta_color="normal" if resumo['saldo_disponivel'] >= 0 else "off"
            )
        with col3:
            st.metric(
                "📅 Média Diária Sugerida",
                f"R$ {resumo['media_diaria_sugerida']:,.2f}",
                help="Valor máximo sugerido para gastos variáveis por dia"
            )

    def _show_breno_progress(self, resumo):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Meta Economia',
            x=['Economia'],
            y=[resumo['meta_economia']],
            marker_color='#00cc96',
            text=f'R$ {resumo["meta_economia"]:,.2f}',
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            name='Economia Real',
            x=['Economia'],
            y=[resumo['total_economia']],
            marker_color='#636efa',
            text=f'R$ {resumo["total_economia"]:,.2f}',
            textposition='auto',
        ))
        fig.update_layout(
            title="Progresso da Meta de Economia",
            barmode='overlay',
            showlegend=True,
            yaxis_title="Valor (R$)"
        )
        st.plotly_chart(fig, use_container_width=True)

    def _show_details(self, resumo):
        st.subheader("📊 Detalhamento do Método")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**📈 Composição da Renda:**")
            st.write(f"- Renda Total: R$ {resumo['total_renda']:,.2f}")
            st.write(f"- Meta Economia (25%): R$ {resumo['meta_economia']:,.2f}")
            st.write(f"- Despesas Fixas: R$ {resumo['total_despesas_fixas']:,.2f}")
            st.write(f"- Saldo Disponível: R$ {resumo['saldo_disponivel']:,.2f}")

        with col2:
            st.write("**🎯 Status das Metas:**")
            status_economia = "✅ Atingida" if resumo['total_economia'] >= resumo['meta_economia'] else "⚠️ Abaixo da Meta"
            st.write(f"- Economia: {status_economia}")
            st.write(f"- Economia Real: R$ {resumo['total_economia']:,.2f}")
            st.write(f"- Diferença: R$ {resumo['economia_real_vs_meta']:,.2f}")


# ---------------------- Instância e execução ----------------------
breno_page = BrenoMethodPage()
breno_page.show_breno_method()
