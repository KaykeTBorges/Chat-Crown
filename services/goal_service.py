from datetime import datetime
from sqlalchemy import and_
from services.database import db_manager

class GoalService:
    def __init__(self):
        self.db = db_manager
    
    def create_goal(self, telegram_id: int, name: str, target_amount: float, 
                   deadline: str, category: str = "Outros", priority: int = 1):
        """Cria uma nova meta financeira"""
        try:
            with self.db.get_session() as session:
                from models.goal import FinancialGoal
                
                goal = FinancialGoal(
                    user_id=telegram_id,
                    name=name,
                    target_amount=target_amount,
                    current_amount=0.0,
                    deadline=datetime.strptime(deadline, '%Y-%m-%d').date(),
                    category=category,
                    priority=priority
                )
                
                session.add(goal)
                session.commit()
                print(f"✅ Meta criada: {name} - R$ {target_amount:.2f}")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao criar meta: {e}")
            return False
    
    def update_goal_progress(self, goal_id: int, current_amount: float):
        """Atualiza o progresso de uma meta"""
        try:
            with self.db.get_session() as session:
                from models.goal import FinancialGoal
                
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                if not goal:
                    return False
                
                goal.current_amount = current_amount
                goal.updated_at = datetime.utcnow()
                session.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao atualizar meta: {e}")
            return False
    
    def delete_goal(self, goal_id: int):
        """Exclui uma meta"""
        try:
            with self.db.get_session() as session:
                from models.goal import FinancialGoal
                
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                if goal:
                    session.delete(goal)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"❌ Erro ao excluir meta: {e}")
            return False
    
    def get_user_goals(self, telegram_id: int, include_completed: bool = True):
        """Busca metas do usuário"""
        try:
            with self.db.get_session() as session:
                from models.goal import FinancialGoal
                
                query = session.query(FinancialGoal).filter(FinancialGoal.user_id == telegram_id)
                
                if not include_completed:
                    # Filtra metas não concluídas (progresso < 100%)
                    query = query.filter(FinancialGoal.current_amount < FinancialGoal.target_amount)
                
                goals = query.order_by(
                    FinancialGoal.priority.desc(),
                    FinancialGoal.deadline.asc()
                ).all()
                
                return [goal.to_dict() for goal in goals]
                
        except Exception as e:
            print(f"❌ Erro ao buscar metas: {e}")
            return []
    
    def get_goal_by_id(self, goal_id: int):
        """Busca uma meta específica"""
        try:
            with self.db.get_session() as session:
                from models.goal import FinancialGoal
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                return goal.to_dict() if goal else None
        except Exception as e:
            print(f"❌ Erro ao buscar meta: {e}")
            return None

# Instância global
goal_service = GoalService()