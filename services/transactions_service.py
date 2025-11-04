from services.database import db_manager
from models.transaction import Transaction

class TransactionService:
    def get_by_id(self, transaction_id):
        with db_manager.get_session() as session:
            return session.query(Transaction).filter(Transaction.id == transaction_id).first()

    def update(self, transaction_id, description=None, amount=None, category=None, type=None, date=None):
        with db_manager.get_session() as session:
            trans = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not trans:
                return False
            
            if description is not None:
                trans.description = description
            if amount is not None:
                trans.amount = amount
            if category is not None:
                trans.category = category
            if type is not None:
                trans.type = type
            if date is not None:
                trans.date = date

            session.commit()
            return True

    def delete(self, transaction_id):
        with db_manager.get_session() as session:
            trans = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not trans:
                return False
            session.delete(trans)
            session.commit()
            return True

transactions_service = TransactionService()
