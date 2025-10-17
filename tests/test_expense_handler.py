# tests/test_expense_handler.py
import pytest
from unittest.mock import AsyncMock
from bot.handlers.expense_handler import handle_expense

# Mock do Update e Context do Telegram
class MockMessage:
    def __init__(self, text, user_id=1):
        self.text = text
        self.reply_text = AsyncMock()
        self.from_user = type("User", (), {"id": user_id})
        self.chat_id = user_id

class MockUpdate:
    def __init__(self, message_text, user_id=1):
        self.message = MockMessage(message_text, user_id)
        self.effective_user = self.message.from_user

class MockContext:
    pass  # não usamos nada de contexto por enquanto

# Lista de mensagens de teste
test_cases = [
    ("50 almoço", 1, True),
    ("120 uber", 2, True),
    ("0 lanche", 3, False),
    ("-30 uber", 4, False),
    (" ", 5, False),
    ("100 algo estranho", 6, True)  # categoria desconhecida
]

@pytest.mark.asyncio
@pytest.mark.parametrize("msg, user_id, should_succeed", test_cases)
async def test_handle_expense(msg, user_id, should_succeed):
    update = MockUpdate(msg, user_id)
    context = MockContext()

    await handle_expense(update, context)

    # Verifica se reply_text foi chamado
    assert update.message.reply_text.called

    response = update.message.reply_text.call_args[0][0]

    if should_succeed:
        assert "✅ Gasto registrado" in response
    else:
        assert "❌" in response
