from datetime import datetime, timedelta
from services.database import db_manager


class FinanceCalculator:
    def __init__(self):
        self.db = db_manager
    
    def get_monthly_summary(self, telegram_id: int, month: int = None, year: int = None):
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        # Load only the transactions for the requested month and user.
        transactions = self._get_monthly_transactions(telegram_id, month, year)
        
        total_renda = sum(t.amount for t in transactions if t.type == 'renda')
        total_despesas_fixas = sum(t.amount for t in transactions if t.type == 'despesa_fixa')
        total_despesas_variaveis = sum(t.amount for t in transactions if t.type == 'despesa_variavel')
        total_economia = sum(t.amount for t in transactions if t.type == 'economia')
        
        total_despesas = total_despesas_fixas + total_despesas_variaveis
        
        meta_economia = total_renda * 0.25
        
        saldo_final = total_renda - total_despesas - total_economia
        saldo_disponivel = total_renda - total_despesas_fixas - meta_economia
        
        economia_real_vs_meta = total_economia - meta_economia
        
        dias_no_mes = self._dias_no_mes(month, year)
        media_diaria_sugerida = saldo_disponivel / dias_no_mes if dias_no_mes > 0 else 0
        
        alertas = []
        
        if total_economia < meta_economia:
            deficit = meta_economia - total_economia
            alertas.append(f"💰 Você está R$ {deficit:.2f} abaixo da meta de economia")
        else:
            superavit = total_economia - meta_economia
            alertas.append(f"🎉 Você superou a meta de economia em R$ {superavit:.2f}!")
        
        if saldo_disponivel < 0:
            alertas.append("⚠️ Suas despesas fixas + meta de economia excedem sua renda!")
        
        if total_despesas_variaveis > saldo_disponivel:
            excesso = total_despesas_variaveis - saldo_disponivel
            alertas.append(f"⚠️ Suas despesas variáveis excederam o orçamento em R$ {excesso:.2f}")
        
        return {
            'periodo': f"{month:02d}/{year}",
            'total_renda': total_renda,
            'total_despesas_fixas': total_despesas_fixas,
            'total_despesas_variaveis': total_despesas_variaveis,
            'total_despesas': total_despesas,
            'total_economia': total_economia,
            'meta_economia': meta_economia,
            'economia_real_vs_meta': economia_real_vs_meta,
            'saldo_final': saldo_final,
            'saldo_disponivel': saldo_disponivel,
            'media_diaria_sugerida': media_diaria_sugerida,
            'dias_no_mes': dias_no_mes,
            'alertas': alertas,
            'transacoes_count': len(transactions)
        }
    
    def _get_monthly_transactions(self, telegram_id: int, month: int, year: int):
        try:
            with self.db.get_session() as session:
                from models.transaction import Transaction

                # Filter by the user's Telegram ID and the month range.
                transactions = (
                    session.query(Transaction)
                    .filter(
                        Transaction.telegram_id == telegram_id,
                        Transaction.date >= f"{year}-{month:02d}-01",
                        Transaction.date <= f"{year}-{month:02d}-{self._dias_no_mes(month, year)}",
                    )
                    .all()
                )
                return transactions
        except Exception as e:
            print(f"❌ Erro ao buscar transações: {e}")
            return []
    
    def _dias_no_mes(self, month: int, year: int):
        if month == 12:
            return (datetime(year + 1, 1, 1) - datetime(year, month, 1)).days
        return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days

    def get_daily_budget_status(self, telegram_id: int, month: int = None, year: int = None):
        """Calculate daily budget status for a given user and month."""
        
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        resumo = self.get_monthly_summary(telegram_id, month, year)
        
        # Current date and basic month info.
        hoje = datetime.now().date()
        primeiro_dia = datetime(year, month, 1).date()
        dias_no_mes = resumo['dias_no_mes']
        dia_do_mes = hoje.day
        
        # Load only variable expenses for the month. We use those to build a day-by-day view.
        transacoes = self._get_monthly_transactions(telegram_id, month, year)
        gastos_variaveis = [t for t in transacoes if t.type == 'despesa_variavel']
        
        # Group variable expenses by day-of-month.
        gastos_por_dia = {}
        for transacao in gastos_variaveis:
            dia = transacao.date.day
            if dia not in gastos_por_dia:
                gastos_por_dia[dia] = 0
            gastos_por_dia[dia] += transacao.amount
        
        # Build a list that the UI can render (one entry per day).
        saldo_disponivel = resumo['saldo_disponivel']
        media_diaria = resumo['media_diaria_sugerida']
        saldo_acumulado = 0
        situacao_dias = []
        
        for dia in range(1, dias_no_mes + 1):
            gasto_dia = gastos_por_dia.get(dia, 0)
            saldo_acumulado += media_diaria - gasto_dia
            
            situacao_dias.append({
                'dia': dia,
                'data': datetime(year, month, dia).strftime('%d/%m'),
                'gasto': gasto_dia,
                'meta_diaria': media_diaria,
                'saldo_acumulado': saldo_acumulado,
                'status': 'futuro' if dia > dia_do_mes else 'hoje' if dia == dia_do_mes else 'passado',
                'ultrapassou': gasto_dia > media_diaria
            })
        
        # Convenience pointer to today's entry (used by alert logic and UI).
        dia_atual = next((d for d in situacao_dias if d['dia'] == dia_do_mes), None)
        
        return {
            'resumo_mensal': resumo,
            'situacao_dias': situacao_dias,
            'dia_atual': dia_atual,
            'saldo_restante_mes': saldo_disponivel - sum(gasto['gasto'] for gasto in situacao_dias),
            'media_ajustada_restante': (saldo_disponivel - sum(gasto['gasto'] for gasto in situacao_dias)) / max(1, dias_no_mes - dia_do_mes),
            'dias_restantes': dias_no_mes - dia_do_mes,
            'total_gasto_variavel_mes': sum(gasto['gasto'] for gasto in situacao_dias)
        }

    def debug_daily_status(self, telegram_id: int, month: int = None, year: int = None):
        """
        Debug helper that prints the structure returned by `get_daily_budget_status`.
        Useful when you are adjusting UI code and want to confirm the returned keys.
        """
        status = self.get_daily_budget_status(telegram_id, month, year)
        print("🔍 DEBUG - Estrutura do daily_status:")
        print(f"Keys: {list(status.keys()) if status else 'None'}")
        if status and 'situacao_dias' in status:
            print(f"Número de dias: {len(status['situacao_dias'])}")
            if status['situacao_dias']:
                print(f"Primeiro dia: {status['situacao_dias'][0]}")
        return status

finance_calculator = FinanceCalculator()