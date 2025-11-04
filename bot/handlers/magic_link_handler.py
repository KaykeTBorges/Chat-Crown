# bot/handlers/magic_link_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from services.database import db_manager
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

async def create_magic_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    token = str(uuid.uuid4())
    now = datetime.utcnow()

    try:
        from models.magic_link import MagicLink
        with db_manager.get_session() as session:
            # 1️⃣ Apaga todos os tokens expirados de todos os usuários
            expired_count = session.query(MagicLink).filter(MagicLink.expires_at < now).delete()
            if expired_count:
                logger.info(f"{expired_count} tokens expirados removidos do banco")
                session.commit()

            # 2️⃣ Apaga tokens antigos do usuário atual (mesmo que não estejam expirados)
            session.query(MagicLink).filter(MagicLink.user_id == user.id).delete()
            session.commit()

            # 3️⃣ Cria o novo token
            magic_link = MagicLink(
                user_id=user.id,
                token=token,
                expires_at=now + timedelta(minutes=15)  # Expira em 15 minutos
            )
            session.add(magic_link)
            session.commit()
        
        # 4️⃣ Monta link para o Streamlit
        from config import config
        link = f"{config.STREAMLIT_URL}?token={token}"
        await update.message.reply_text(
            f"🔗 Aqui está seu link seguro para acessar suas transações:\n{link}"
        )
        logger.info(f"Magic link criado para user_id={user.id}")

    except Exception as e:
        logger.error(f"Erro ao criar magic link: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao criar o link. Tente novamente.")
