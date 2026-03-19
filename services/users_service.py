from services.database import db_manager
from models.user import User
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class UsersService:
    @staticmethod
    def get_or_create_user(telegram_user_data):
        """
        Get a user by Telegram ID, or create it if it does not exist yet.

        `telegram_user_data` is expected to be the object returned by Telegram
        (it can be a dict-like object that has keys like "id", "username", etc).
        """
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_user_data.get('id')).first()

            if user:
                # Keep the database in sync with Telegram profile changes (username/name).
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
                    user.updated_at = datetime.now(timezone.utc)
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Usuário atualizado: {user.telegram_id} - {user.username}")
                return user

            # Create a new local record for this Telegram user.
            user = User(
                telegram_id=telegram_user_data.get('id'),
                username=telegram_user_data.get('username'),
                first_name=telegram_user_data.get('first_name'),
                last_name=telegram_user_data.get('last_name'),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Novo usuário criado: {user.telegram_id} - {user.username}")
            return user

    @staticmethod
    def get_user_by_telegram_id(telegram_id: int):
        """
        Fetch a user using the Telegram ID as the main key.
        This is the method the Streamlit app should use after login.
        """
        with db_manager.get_session() as session:
            return session.query(User).filter_by(telegram_id=telegram_id).first()

# Global instance for convenience imports across the project.
users_service = UsersService()