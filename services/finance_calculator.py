from datetime import datetime, timedelta
from services.database import db_manager

class FinanceCalculator:
    def __init__(self):
        self.db = db_manager
    
    def get_monthly_summary(self, user_id: int, month: int = None, year: int = None):
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        transactions = self._get_monthly_transactions(user_id, month, year)
        
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
    
    def _get_monthly_transactions(self, user_id: int, month: int, year: int):
        try:
            with self.db.get_session() as session:
                from models.transaction import Transaction
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= f"{year}-{month:02d}-01",
                    Transaction.date <= f"{year}-{month:02d}-{self._dias_no_mes(month, year)}"
                ).all()
                return transactions
        except Exception as e:
            print(f"❌ Erro ao buscar transações: {e}")
            return []
    
    def _dias_no_mes(self, month: int, year: int):
        if month == 12:
            return (datetime(year + 1, 1, 1) - datetime(year, month, 1)).days
        return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days

finance_calculator = FinanceCalculator()