from datetime import datetime
from sqlalchemy import and_
from services.database import db_manager

class BudgetService:
    def __init__(self):
        self.db = db_manager
    
    def set_budget(self, user_id: int, category: str, monthly_limit: float, month: int = None, year: int = None):
        """Define orçamento para uma categoria"""
        month = month or datetime.now().month
        year = year or datetime.now().year
        
        try:
            with self.db.get_session() as session:
                from models.budget import Budget
                
                # Verificar se já existe orçamento
                budget = session.query(Budget).filter(
                    Budget.user_id == user_id,
                    Budget.category == category,
                    Budget.month == month,
                    Budget.year == year
                ).first()
                
                if budget:
                    budget.monthly_limit = monthly_limit
                else:
                    budget = Budget(
                        user_id=user_id,
                        category=category,
                        monthly_limit=monthly_limit,
                        month=month,
                        year=year
                    )
                    session.add(budget)
                
                session.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao definir orçamento: {e}")
            return False
    
    def get_budgets_with_status(self, user_id: int, month: int = None, year: int = None):
        """Retorna orçamentos com status calculado"""
        month = month or datetime.now().month
        year = year or datetime.now().year
        
        try:
            with self.db.get_session() as session:
                from models.budget import Budget
                from models.transaction import Transaction
                
                # Buscar orçamentos do mês
                budgets = session.query(Budget).filter(
                    Budget.user_id == user_id,
                    Budget.month == month,
                    Budget.year == year
                ).all()
                
                if not budgets:
                    return {'budgets': [], 'alerts': []}
                
                # Buscar transações do mês
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1}-01-01"
                else:
                    end_date = f"{year}-{month+1:02d}-01"
                
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date < end_date,
                    Transaction.type.in_(['despesa_fixa', 'despesa_variavel'])
                ).all()
                
                # Calcular gastos por categoria
                category_spending = {}
                for transaction in transactions:
                    if transaction.category not in category_spending:
                        category_spending[transaction.category] = 0
                    category_spending[transaction.category] += transaction.amount
                
                # Combinar dados
                result = []
                alerts = []
                
                for budget in budgets:
                    spent = category_spending.get(budget.category, 0)
                    remaining = budget.monthly_limit - spent
                    usage_percentage = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
                    
                    budget_data = {
                        'id': budget.id,
                        'category': budget.category,
                        'monthly_limit': budget.monthly_limit,
                        'spent': spent,
                        'remaining': remaining,
                        'usage_percentage': usage_percentage,
                        'alert_level': 'safe'
                    }
                    
                    # Definir alertas
                    if usage_percentage >= 100:
                        budget_data['alert_level'] = 'exceeded'
                        alerts.append(f"🚨 {budget.category}: Orçamento estourado!")
                    elif usage_percentage >= 80:
                        budget_data['alert_level'] = 'warning'
                        alerts.append(f"⚠️ {budget.category}: {usage_percentage:.0f}% usado")
                    
                    result.append(budget_data)
                
                return {
                    'budgets': result,
                    'alerts': alerts
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar orçamentos: {e}")
            return {'budgets': [], 'alerts': []}

# Instância global
budget_service = BudgetService()