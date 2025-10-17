from telegram import Update
from telegram.ext import ContextTypes
from services.expense_service import ExpenseService

expense_service = ExpenseService()

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    summary = expense_service.get_mothly_summary(user_id)

    if not summary:
        await update.message.reply_text("📭 Você ainda não registrou nenhum gasto neste mês.")
        return

    msg_lines = [
        f"📊 RESUMO DE {summary['month']}/{summary['year']}",
        f"\n💰 Total Gasto: R$ {summary['total']:.2f}\n",
        "📂 Por Categoria:"
    ]

    for cat, data in summary['categories'].items():
        msg_lines.append(f"{data['emoji']} {cat}: R$ {data['total']:.2f} ({data['percent']:.1f}%)")

    msg_lines.append(f"\n📈 Média diária: R$ {summary['daily_avg']:.2f}")

    await update.message.reply_text("\n".join(msg_lines))