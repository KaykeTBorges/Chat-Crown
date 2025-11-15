# bot/handlers/help_handler.py
from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /ajuda"""
    help_text = """
🤖 *COMANDOS DO BOT FINANCEIRO*

📊 *Comandos Principais:*
/start - Inicia o bot e mostra as boas-vindas.
/ajuda - Exibe esta mensagem de ajuda.
/login - Gera um código para acessar o painel web.
/resumo - Mostra um resumo financeiro detalhado do mês.
/listar - Lista suas transações com opções de editar e excluir.

💰 *Registro de Gastos (Inteligente):*
Apenas escreva naturalmente. Exemplos:
• `almoço 45,50`
• `aluguel 1500`
• `mercado 350`
• `gasolina 120`
• `investi 1000` (será categorizado como 'economia')
• `recebi 5000` (será categorizado como 'renda')

🛠️ *Como Editar/Excluir:*
1. Use `/listar` para ver suas transações.
2. Clique em "✏️ Editar" ou "🗑️ Excluir" ao lado de cada item.
3. Siga as instruções na tela.

*Desenvolvido para facilitar sua vida financeira!* 🎯
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')