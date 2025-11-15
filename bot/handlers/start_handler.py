# bot/handlers/start_handler.py
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    user = update.effective_user
    
    welcome_text = f"""
👋 Olá, {user.first_name}!

Bem-vindo ao seu *Assistente Financeiro Pessoal*! 🏆

Aqui você pode gerenciar suas finanças de forma simples e rápida.

💡 *Comandos Principais:*
• `/login` - Receba um código para acessar o painel web.
• `/resumo` - Veja um resumo financeiro completo do seu mês.
• `/listar` - Liste todas as transações do mês para editar ou excluir.

💰 *Registrar Gastos:*
• Apenas escreva: `almoço 45,50` ou `salário 5000`
• O bot identifica automaticamente a categoria e o valor.

Vamos organizar suas finanças juntos! 💰
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')
    logger.info(f"Usuário {user.id} ({user.first_name}) iniciou o bot")