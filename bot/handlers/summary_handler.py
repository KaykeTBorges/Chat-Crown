# bot/handlers/summary_handler.py
from telegram import Update
from telegram.ext import ContextTypes
import logging
from services.finance_calculator import finance_calculator
from services.users_service import UsersService # ✅ importar UsersService

logger = logging.getLogger(__name__)

async def summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /resumo command and send a monthly financial summary."""
    
    try:
        # Ensure the Telegram user exists in the database and get the model instance.
        user = UsersService.get_or_create_user(update.effective_user)

        # Use the Telegram ID consistently (all services filter by telegram_id).
        resumo = finance_calculator.get_monthly_summary(user.telegram_id) 
        
        if resumo['transacoes_count'] == 0:
            await update.message.reply_text(
                "📊 *RESUMO FINANCEIRO*\n\n"
                "Ainda não há transações registradas este mês.\n\n"
                "💡 *Registre suas primeiras transações:*\n"
                "• `salário 5000` - Para renda\n"
                "• `aluguel 1500` - Para despesa fixa\n" 
                "• `mercado 350` - Para despesa variável\n"
                "• `investi 1000` - Para economia",
                parse_mode='Markdown'
            )
            return
        
        status_economia = "✅" if resumo['economia_real_vs_meta'] >= 0 else "❌"
        sinal_economia = "+" if resumo['economia_real_vs_meta'] >= 0 else ""
        
        response = f"""
📊 *RESUMO FINANCEIRO - {resumo['periodo']}*

💰 *ENTRADAS (Renda):* R$ {resumo['total_renda']:,.2f}

🔴 *SAÍDAS FIXAS:* R$ {resumo['total_despesas_fixas']:,.2f}
🟡 *SAÍDAS VARIÁVEIS:* R$ {resumo['total_despesas_variaveis']:,.2f}
💸 *TOTAL SAÍDAS:* R$ {resumo['total_despesas']:,.2f}

🚀 *ECONOMIA REAL:* R$ {resumo['total_economia']:,.2f}
🎯 *META ECONOMIA (25%):* R$ {resumo['meta_economia']:,.2f}
{status_economia} *ECONOMIA vs META:* {sinal_economia}R$ {resumo['economia_real_vs_meta']:,.2f}

⚖️ *SALDO FINAL:* R$ {resumo['saldo_final']:,.2f}

📈 *MÉTODO BRENO NOGUEIRA:*
• Disponível para gastos variáveis: R$ {resumo['saldo_disponivel']:,.2f}
• Média diária sugerida: R$ {resumo['media_diaria_sugerida']:,.2f}
• Dias no mês: {resumo['dias_no_mes']}
"""
        
        if resumo['alertas']:
            response += "\n\n⚠️ *ALERTAS:*\n• " + "\n• ".join(resumo['alertas'])
        
        response += f"\n\n📝 *Total de transações:* {resumo['transacoes_count']}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando /resumo: {e}")
        await update.message.reply_text(
            "❌ Erro ao gerar resumo. Verifique se há transações registradas.",
            parse_mode='Markdown'
        )