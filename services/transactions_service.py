# services/transactions_service.py
import pandas as pd
from datetime import datetime, timedelta
from services.database import db_manager
from models.transaction import Transaction
from services.ai_processor import ai_processor

class TransactionsService:
    def __init__(self):
        # Default categories used by the text processor.
        self.categories = ai_processor.categories

    # ---------------- CRUD ----------------
    def get_transactions(self, telegram_id: int, filters=None, page: int = 0, items_per_page: int = 25):
        """
        Return transactions for a user, after applying filters, sorting and pagination.
        """
        filters = filters or {}
        transactions = self._get_all_transactions(telegram_id)

        # Apply filters in memory.
        transactions = self._apply_search(transactions, filters.get("search_term"))
        transactions = self._apply_category_filter(transactions, filters.get("category"))
        transactions = self._apply_type_filter(transactions, filters.get("type"))
        transactions = self._apply_date_filter(transactions, filters.get("date_range"))

        # Then apply sorting.
        transactions = self._apply_sort(transactions, filters.get("sort_by"))

        # Finally, calculate pagination slice.
        total_pages = max(1, (len(transactions) + items_per_page - 1) // items_per_page)
        start = page * items_per_page
        end = start + items_per_page
        return transactions[start:end], total_pages

    def _get_all_transactions(self, telegram_id: int):
        try:
            with db_manager.get_session() as session:
                return session.query(Transaction).filter(Transaction.telegram_id == telegram_id).all()
        except Exception as e:
            print(f"❌ Error while fetching transactions: {e}")
            return []

    def create(self, telegram_id: int, description: str, amount: float, category: str, type: str, date, detected_by: str = "manual"):
        try:
            with db_manager.get_session() as session:
                t = Transaction(
                    telegram_id=telegram_id,
                    description=description,
                    amount=amount,
                    category=category,
                    type=type,
                    date=date,
                    detected_by=detected_by
                )
                session.add(t)
                session.commit()
                session.refresh(t)
                return t
        except Exception as e:
            print(f"❌ Error while creating transaction: {e}")
            return None

    def update(self, transaction_id: int, **kwargs):
        try:
            with db_manager.get_session() as session:
                t = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if not t:
                    return False
                for key, value in kwargs.items():
                    if hasattr(t, key):
                        setattr(t, key, value)
                session.commit()
                return True
        except Exception as e:
            print(f"❌ Error while updating transaction: {e}")
            return False

    def delete(self, transaction_id):
        try:
            with db_manager.get_session() as session:
                t = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if t:
                    session.delete(t)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"❌ Error while deleting transaction: {e}")
            return False

    def get_by_id(self, transaction_id: int):
        """
        Fetch a single transaction by its ID.

        This is important for edit/delete flows that start from a selected record.
        """
        try:
            with db_manager.get_session() as session:
                return session.query(Transaction).filter(Transaction.id == transaction_id).first()
        except Exception as e:
            print(f"❌ Error while fetching transaction by ID: {e}")
            return None

    # ---------------- Filters ----------------
    def _apply_search(self, transactions, search_term):
        if search_term:
            term = search_term.lower()
            return [t for t in transactions if term in t.description.lower()]
        return transactions

    def _apply_category_filter(self, transactions, category):
        if category and category != "Todas":
            return [t for t in transactions if t.category == category]
        return transactions

    def _apply_type_filter(self, transactions, type_filter):
        if type_filter and type_filter != "Todos":
            return [t for t in transactions if t.type == type_filter]
        return transactions

    def _apply_date_filter(self, transactions, date_range):
        if not date_range:
            return transactions
        today = datetime.now().date()
        ranges = {
            '7_days': today - timedelta(days=7),
            '30_days': today - timedelta(days=30),
            '90_days': today - timedelta(days=90),
            'current_month': today.replace(day=1),
            'last_month': (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            'all_time': datetime.min.date()
        }
        start_date = ranges.get(date_range, datetime.min.date())
        result = []
        for t in transactions:
            t_date = t.date
            if isinstance(t_date, str):
                t_date = datetime.strptime(t_date, "%Y-%m-%d").date()
            if t_date >= start_date:
                result.append(t)
        return result

    def _apply_sort(self, transactions, sort_by):
        if not sort_by:
            sort_by = "date_desc"
        key_funcs = {
            'date_desc': lambda t: t.date,
            'date_asc': lambda t: t.date,
            'amount_desc': lambda t: t.amount,
            'amount_asc': lambda t: t.amount,
            'description_asc': lambda t: t.description.lower()
        }
        reverse = sort_by in ['date_desc', 'amount_desc']
        return sorted(transactions, key=key_funcs.get(sort_by, lambda t: t.date), reverse=reverse)

    def get_recent_transactions(self, telegram_id: int, limit: int = 5):
        with db_manager.get_session() as session:
            return (
                session.query(Transaction)
                .filter(Transaction.telegram_id == telegram_id)
                .order_by(Transaction.date.desc())
                .limit(limit)
                .all()
            )

# Global instance to be used across the project.
transactions_service = TransactionsService()
