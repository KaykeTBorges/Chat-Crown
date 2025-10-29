from telegram import Update
from telegram.ext import ContextTypes
import logging
from services.ai_processor import ai_processor
from services.database import db_manager
from datetime import datetime

logger = logging.getLogger(__name__)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens de texto (registro de despesas)"""
    user_message = update.message.text
    user = update.effective_user
    
    try:
        # Processar a mensagem com IA
        expense_data = ai_processor.detect_expense(user_message)
        
        # Verificar se conseguiu extrair um valor
        if expense_data['amount'] is None:
            await update.message.reply_text(
                "❌ Não consegui identificar o valor na sua mensagem.\n\n"
                "💡 *Formatos que entendo:*\n"
                "• `almoço 45,50`\n" 
                "• `aluguel 1500`\n"
                "• `R$ 35,00 mercado`\n"
                "• `100 uber`\n"
                "• `investi 1000`",
                parse_mode='Markdown'
            )
            return
        
        # Salvar no banco de dados
        transaction = db_manager.create_transaction(
            user_id=user.id,
            amount=expense_data['amount'],
            category=expense_data['category'],
            description=expense_data['description'],
            transaction_type=expense_data['type'],
            detected_by=expense_data['detected_by']
        )
        
        if not transaction:
            await update.message.reply_text("❌ Erro ao salvar transação no banco.")
            return
        
        # Preparar resposta de confirmação
        emoji_map = {
            # RENDAS (Entradas)
            'Salário': '💰',
            'Freela': '💼', 
            'Investimentos': '📈',
            'Outros': '🎯',
            # DESPESAS FIXAS (Saídas)
            'Moradia': '🏠',
            'Transporte': '🚗',
            'Saúde': '💊',
            'Educação': '📚',
            'Seguros': '🛡️',
            'Dívidas': '💳',
            # DESPESAS VARIÁVEIS (Saídas)
            'Alimentação': '🍽️',
            'Lazer': '🎮',
            'Vestuário': '👕',
            'Diversos': '📦',
            # ECONOMIA (Guardar dinheiro)
            'Investimentos': '🚀',
            'Poupança': '🐷',
            'Fundos': '📊',
            'Previdência': '👵'
        }
        
        # Definir cores e textos baseados no tipo
        if expense_data['type'] == 'renda':
            header = "💰 *ENTRADA REGISTRADA!*"
            type_text = "RENDA"
            color_emoji = "🟢"
        elif expense_data['type'] == 'economia':
            header = "🚀 *ECONOMIA REGISTRADA!*"
            type_text = "ECONOMIA/INVESTIMENTO"
            color_emoji = "🔵"
        else:
            header = "💸 *SAÍDA REGISTRADA!*" 
            type_text = "DESPESA"
            if expense_data['type'] == 'despesa_fixa':
                type_text += " FIXA"
                color_emoji = "🔴"
            else:
                type_text += " VARIÁVEL"
                color_emoji = "🟡"
        
        emoji = emoji_map.get(expense_data['category'], '💸')
        
        response = f"""
{header}

{emoji} *Categoria:* {expense_data['category']}
💵 *Valor:* R$ {expense_data['amount']:.2f}
📝 *Descrição:* {expense_data['description']}
📊 *Tipo:* {type_text} {color_emoji}

🕒 *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
🤖 *Detectado por:* {expense_data['detected_by'].upper()}
    """
        
        # Adicionar mensagem especial para economia
        if expense_data['type'] == 'economia':
            response += "\n\n💡 *Parabéns! Você está construindo seu futuro financeiro!*"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Log da transação
        logger.info(f"Transação registrada: Usuário {user.id} - {expense_data['category']} - R$ {expense_data['amount']:.2f}")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text(
            "❌ Ocorreu um erro ao processar sua mensagem.\n"
            "💡 Tente novamente ou use o formato: `almoço 45,50`",
            parse_mode='Markdown'
        )