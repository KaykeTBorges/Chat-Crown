from services.database import db_manager
from models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UsersService:
    @staticmethod
    def get_or_create_user(telegram_user):
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_user.id).first()

            if user:
                updated = False
                if user.username != telegram_user.username:
                    user.username = telegram_user.username
                    updated = True
                if user.first_name != telegram_user.first_name:
                    user.first_name = telegram_user.first_name
                    updated = True
                if user.last_name != telegram_user.last_name:
                    user.last_name = telegram_user.last_name
                    updated = True
                if updated:
                    user.updated_at = datetime.utcnow()
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Usuário atualizado: {user.telegram_id} - {user.username}")
                return user

            # Cria novo usuário
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Novo usuário criado: {user.telegram_id} - {user.username}")
            return user

    @staticmethod
    def get_user_by_id(user_id):
        with db_manager.get_session() as session:
            return session.query(User).filter_by(id=user_id).first()
