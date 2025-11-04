# services/transactions_service.py
import pandas as pd
from datetime import datetime, timedelta
from services.database import db_manager
from models.transaction import Transaction
from services.ai_processor import ai_processor

class TransactionsService:
    def __init__(self):
        self.categories = ai_processor.categories  # categorias padrão

    # ---------------- CRUD ----------------
    def get_transactions(self, user_id, filters=None, page=0, items_per_page=25):
        """
        Retorna transações filtradas, ordenadas e paginadas.
        """
        filters = filters or {}
        transactions = self._get_all_transactions(user_id)

        # filtros
        transactions = self._apply_search(transactions, filters.get("search_term"))
        transactions = self._apply_category_filter(transactions, filters.get("category"))
        transactions = self._apply_type_filter(transactions, filters.get("type"))
        transactions = self._apply_date_filter(transactions, filters.get("date_range"))

        # ordenação
        transactions = self._apply_sort(transactions, filters.get("sort_by"))

        # paginação
        total_pages = max(1, (len(transactions) + items_per_page - 1) // items_per_page)
        start = page * items_per_page
        end = start + items_per_page
        return transactions[start:end], total_pages

    def _get_all_transactions(self, user_id):
        try:
            with db_manager.get_session() as session:
                return session.query(Transaction).filter(Transaction.user_id == user_id).all()
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return []

    def create(self, user_id, description, amount, category, type, date, detected_by="manual"):
        try:
            with db_manager.get_session() as session:
                t = Transaction(
                    user_id=user_id,
                    description=description,
                    amount=amount,
                    category=category,
                    type=type,
                    date=date,
                    detected_by=detected_by
                )
                session.add(t)
                session.commit()
                return t
        except Exception as e:
            print(f"Erro ao criar transação: {e}")
            return None

    def update(self, transaction_id, **kwargs):
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
            print(f"Erro ao atualizar transação: {e}")
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
            print(f"Erro ao excluir transação: {e}")
            return False

    # ---------------- Filtros ----------------
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

    # ---------------- Import / Export ----------------
    def import_from_dataframe(self, user_id, df):
        try:
            required = {"data", "descricao", "valor", "categoria", "tipo"}
            if not required.issubset(set(df.columns)):
                raise ValueError("Colunas obrigatórias ausentes")
            
            df.columns = [c.lower().strip() for c in df.columns]
            
            with db_manager.get_session() as session:
                for _, row in df.iterrows():
                    t = Transaction(
                        user_id=user_id,
                        description=row["descricao"],
                        amount=float(row["valor"]),
                        category=row["categoria"],
                        type=row["tipo"],
                        date=pd.to_datetime(row["data"]).date(),
                        detected_by="upload"
                    )
                    session.add(t)
                session.commit()
            return True
        except Exception as e:
            print(f"Erro ao importar transações: {e}")
            return False

    def export(self, transactions, format="csv"):
        if not transactions:
            return None
        df = pd.DataFrame([{
            'Data': t.date.strftime("%d/%m/%Y") if isinstance(t.date, datetime) else t.date,
            'Tipo': t.type,
            'Categoria': t.category,
            'Descrição': t.description,
            'Valor': t.amount,
            'Detectado por': t.detected_by
        } for t in transactions])
        if format == "csv":
            return df.to_csv(index=False, sep=";", encoding="utf-8")
        elif format == "json":
            return df.to_json(orient="records", force_ascii=False)
        else:
            return None

    def get_recent_transactions(self, user_id: int, limit: int = 5):
        with db_manager.get_session() as session:
            return (
                session.query(Transaction)
                .filter(Transaction.user_id == user_id)
                .order_by(Transaction.date.desc())
                .limit(limit)
                .all()
            )

# instancia global
transactions_service = TransactionsService()
