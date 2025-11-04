from services.database import db_manager
from models.user import User

class UsersService:
    @staticmethod
    def get_or_create_user(telegram_user):
        with db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_user.id).first()
            if not user:
                user = User(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
    
    @staticmethod
    def get_user_by_id(user_id):
        with db_manager.get_session() as session:
            return session.query(User).filter_by(id=user_id).first()
