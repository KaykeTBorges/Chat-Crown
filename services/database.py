from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect
from config import config
import time

class DatabaseManager:
    def __init__(self):
        self.database_url = config.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self.setup_engine()
    
    def setup_engine(self):
        """Setup database engine with proper configuration"""
        try:
            if "supabase" in self.database_url or "postgresql" in self.database_url:
                self.engine = create_engine(
                    self.database_url,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,
                    echo=False
                )
            else:
                self.database_url = "sqlite:///./finance.db"
                self.engine = create_engine(self.database_url)
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print(f"✅ Database engine configured for: {self.database_url}")
            
        except Exception as e:
            print(f"❌ Error setting up database engine: {e}")
            self._setup_fallback()
    
    def _setup_fallback(self):
        """Fallback to SQLite"""
        print("🔄 Setting up SQLite fallback...")
        self.database_url = "sqlite:///./finance.db"
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables in the database if they don't exist - CORRIGIDO"""
        from models.base import Base
        
        try:
            # CORREÇÃO: Usar inspect() em vez de dialect.has_table()
            inspector = inspect(self.engine)
            existing_tables = inspector.has_table('users')  # Verifica se a tabela users existe
            
            # Create all tables (only creates missing ones)
            Base.metadata.create_all(bind=self.engine)
            
            if existing_tables:
                print("✅ Database tables verified! (already exist)")
            else:
                print("✅ Database tables created successfully!")
                
            return True
        except Exception as e:
            print(f"❌ Error with tables: {e}")
            return False
        
    def test_connection(self, retries=3, delay=2):
        """Test the database connection with retries"""
        for attempt in range(retries):
            try:
                with self.get_session() as session:
                    # Use text() for explicit SQL in SQLAlchemy 2.0
                    session.execute(text("SELECT 1"))
                print("✅ Database connection established!")
                return True
            except OperationalError as e:
                print(f"❌ Database connection error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("🔄 Switching to SQLite fallback...")
                    self._setup_fallback()
                    return self.test_connection()
            except Exception as e:
                print(f"❌ Unexpected database error: {e}")
                return False

    def create_transaction(self, user_id: int, amount: float, category: str, 
                          description: str, transaction_type: str, detected_by: str = "manual"):
        """Cria uma nova transação no banco"""
        from models.transaction import Transaction
        from datetime import datetime
        
        try:
            with self.get_session() as session:
                transaction = Transaction(
                    user_id=user_id,
                    type=transaction_type,
                    amount=amount,
                    category=category,
                    description=description,
                    date=datetime.now().date(),
                    detected_by=detected_by
                )
                session.add(transaction)
                session.commit()
                print(f"✅ Transação salva: {category} - R$ {amount:.2f}")
                return transaction
        except Exception as e:
            print(f"❌ Erro ao salvar transação: {e}")
            return None

    def get_user_transactions(self, user_id: int, days: int = 30):
        """Busca transações de um usuário dos últimos N dias"""
        from models.transaction import Transaction
        from datetime import datetime, timedelta
        
        try:
            with self.get_session() as session:
                start_date = datetime.now().date() - timedelta(days=days)
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date
                ).order_by(Transaction.date.desc()).all()
                return transactions
        except Exception as e:
            print(f"❌ Erro ao buscar transações: {e}")
            return []

    # === NOVOS MÉTODOS PARA EDIÇÃO ===
    def update_transaction(self, transaction_id: int, **kwargs):
        """Atualiza uma transação existente"""
        try:
            with self.get_session() as session:
                from models.transaction import Transaction
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if transaction:
                    for key, value in kwargs.items():
                        if hasattr(transaction, key):
                            setattr(transaction, key, value)
                    session.commit()
                    print(f"✅ Transação {transaction_id} atualizada")
                    return True
                return False
        except Exception as e:
            print(f"❌ Erro ao atualizar transação: {e}")
            return False

    def delete_transaction(self, transaction_id: int):
        """Exclui uma transação"""
        try:
            with self.get_session() as session:
                from models.transaction import Transaction
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if transaction:
                    session.delete(transaction)
                    session.commit()
                    print(f"✅ Transação {transaction_id} excluída")
                    return True
                return False
        except Exception as e:
            print(f"❌ Erro ao excluir transação: {e}")
            return False

    def get_transaction_by_id(self, transaction_id: int):
        """Busca uma transação específica pelo ID"""
        try:
            with self.get_session() as session:
                from models.transaction import Transaction
                return session.query(Transaction).filter(Transaction.id == transaction_id).first()
        except Exception as e:
            print(f"❌ Erro ao buscar transação: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager()