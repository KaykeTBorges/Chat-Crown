import logging
from datetime import datetime
from sqlalchemy import and_
from services.database import db_manager
from models.financial_goal import FinancialGoal

logger = logging.getLogger(__name__)


class GoalService:
    def __init__(self):
        self.db = db_manager
    
    def create_goal(self, telegram_id: int, name: str, target_amount: float, 
                   deadline: str, category: str = "Outros", priority: int = 1):
        """Create a new financial goal for the given Telegram user."""
        try:
            with self.db.get_session() as session:

                # Goals are linked to the user using the Telegram ID.
                goal = FinancialGoal(
                    telegram_id=telegram_id,
                    name=name,
                    target_amount=target_amount,
                    current_amount=0.0,
                    deadline=datetime.strptime(deadline, "%Y-%m-%d").date(),
                    category=category,
                    priority=priority,
                )
                
                session.add(goal)
                session.commit()
                logger.info(f"Meta criada: {name} - R$ {target_amount:.2f}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao criar meta: {e}")
            return False
    
    def update_goal_progress(self, goal_id: int, current_amount: float):
        """Update the saved progress of a specific goal."""
        try:
            with self.db.get_session() as session:

                
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                if not goal:
                    return False
                
                goal.current_amount = current_amount
                goal.updated_at = datetime.utcnow()
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erro ao atualizar meta: {e}")
            return False
    
    def delete_goal(self, goal_id: int):
        """Delete a goal by its ID."""
        try:
            with self.db.get_session() as session:

                
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                if goal:
                    session.delete(goal)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Erro ao excluir meta: {e}")
            return False
    
    def get_user_goals(self, telegram_id: int, include_completed: bool = True):
        """Return all goals for a user, optionally skipping completed ones."""
        try:
            with self.db.get_session() as session:


                query = session.query(FinancialGoal).filter(FinancialGoal.telegram_id == telegram_id)
                
                if not include_completed:
                    # Skip completed goals (progress < 100%).
                    query = query.filter(FinancialGoal.current_amount < FinancialGoal.target_amount)
                
                goals = query.order_by(
                    FinancialGoal.priority.desc(),
                    FinancialGoal.deadline.asc()
                ).all()
                
                return [goal.to_dict() for goal in goals]
                
        except Exception as e:
            logger.error(f"Erro ao buscar metas: {e}")
            return []
    
    def get_goal_by_id(self, goal_id: int):
        """Fetch a single goal by its database ID."""
        try:
            with self.db.get_session() as session:
                from models.financial_goal import FinancialGoal
                goal = session.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
                return goal.to_dict() if goal else None
        except Exception as e:
            logger.error(f"Erro ao buscar meta: {e}")
            return None

# Global instance so other modules can import `goal_service` directly.
goal_service = GoalService()