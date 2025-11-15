# api/main.py
from fastapi import FastAPI, HTTPException, Form
import random
import string
import time

app = FastAPI(title="Chat Crown Auth API (Simplified)")

# Armazenamento temporário dos códigos.
# Em produção, USE REDIS ou um banco de dados com expiração.
# Formato: {"123456": 123456789, "654321": 987654321}
LOGIN_CODES = {}

def generate_code() -> str:
    """Gera um código de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=6))

@app.post("/auth/generate_code")
async def generate_login_code(telegram_id: int = Form(...)):
    """
    Endpoint para o BOT gerar um código de login para um usuário.
    """
    # Remove códigos antigos deste usuário, se houver
    old_code_to_remove = None
    for code, user_id in LOGIN_CODES.items():
        if user_id == telegram_id:
            old_code_to_remove = code
            break
    if old_code_to_remove:
        LOGIN_CODES.pop(old_code_to_remove)

    # Gera e armazena o novo código
    new_code = generate_code()
    LOGIN_CODES[new_code] = telegram_id
    
    print(f"Código gerado: {new_code} para o telegram_id: {telegram_id}") # Log para debug
    
    return {"status": "success", "code": new_code}

@app.post("/auth/validate_code")
async def validate_login_code(code: str = Form(...)):
    """
    Endpoint para o Streamlit validar um código de login.
    """
    telegram_id = LOGIN_CODES.pop(code, None) # pop() garante que o código seja de uso único

    if telegram_id:
        print(f"Código {code} validado para o telegram_id: {telegram_id}") # Log para debug
        return {"status": "success", "telegram_id": telegram_id}
    else:
        print(f"Código {code} inválido ou já usado.") # Log para debug
        raise HTTPException(status_code=404, detail="Código inválido ou expirado.")
