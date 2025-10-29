from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    user = update.effective_user
    
    welcome_text = f"""
👋 Olá {user.first_name}!

Bem-vindo ao seu Assistente Financeiro Pessoal!

💡 *Como usar:*
• Escreva suas despesas naturalmente: "almoço 45,50" ou "aluguel 1500"
• Use comandos para ações específicas

📋 *Comandos Disponíveis:*
/ajuda - Ver todos os comandos
/resumo - Resumo financeiro mensal

🔮 *Em Breve:*
/editar - Editar transações
/orcamento - Definir orçamentos por categoria
/economia - Acompanhar investimentos

Vamos organizar suas finanças juntos! 💰
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    # Log do usuário
    logger.info(f"Usuário {user.id} ({user.first_name}) iniciou o bot")