# services/users_service.py

from services.database import db_manager
from models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UsersService:
    @staticmethod
    def get_or_create_user(telegram_user_data):
        """
        Busca um usuário pelo telegram_id. Se não existir, cria um novo.
        'telegram_user_data' é o dicionário que vem do widget do Telegram.
        """
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_user_data.get('id')).first()

            if user:
                # Atualiza dados caso tenham mudado (ex: nome de usuário)
                updated = False
                if user.username != telegram_user_data.get('username'):
                    user.username = telegram_user_data.get('username')
                    updated = True
                if user.first_name != telegram_user_data.get('first_name'):
                    user.first_name = telegram_user_data.get('first_name')
                    updated = True
                if user.last_name != telegram_user_data.get('last_name'):
                    user.last_name = telegram_user_data.get('last_name')
                    updated = True
                if updated:
                    user.updated_at = datetime.utcnow()
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Usuário atualizado: {user.telegram_id} - {user.username}")
                return user

            # Cria novo usuário
            user = User(
                telegram_id=telegram_user_data.get('id'),
                username=telegram_user_data.get('username'),
                first_name=telegram_user_data.get('first_name'),
                last_name=telegram_user_data.get('last_name'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Novo usuário criado: {user.telegram_id} - {user.username}")
            return user

    @staticmethod
    def get_user_by_telegram_id(telegram_id: int):
        """
        Busca um usuário usando o telegram_id como chave.
        Este é o método principal que o Streamlit usará.
        """
        with db_manager.get_session() as session:
            return session.query(User).filter_by(telegram_id=telegram_id).first()

# Instância global para fácil acesso
users_service = UsersService()