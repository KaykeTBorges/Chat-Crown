from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /ajuda"""
    help_text = """
🤖 *COMANDOS DO BOT FINANCEIRO*

📊 *Comandos Básicos:*
/start - Iniciar o bot
/ajuda - Esta mensagem de ajuda
/resumo - Resumo financeiro mensal
/minhas-transacoes - Link para acessar suas transações

💰 *Registro de Gastos:*
Apenas escreva naturalmente:
• "almoço 45,50"
• "aluguel 1500"
• "mercado 350"
• "gasolina 120"
• "investi 1000"
• "salário 5000"

🎯 *Método Breno Nogueira:*
Aplicação automática da regra dos 25% de economia
Metas de gastos diários
Orçamento por categorias

🛠️ *Funcionalidades em Breve:*
/editar - Editar transações
/orcamento - Definir orçamentos
/economia - Acompanhar investimentos
/relatorio - Relatórios detalhados

*Desenvolvido especialmente para você!* 🎯
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')