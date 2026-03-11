# api/main.py
from fastapi import FastAPI, HTTPException, Form
import random
import string

app = FastAPI(title="Chat Crown Auth API (Simplified)")

# In-memory storage for short-lived login codes.
LOGIN_CODES = {}

def generate_code() -> str:
    """Generate a 6-digit code"""
    return ''.join(random.choices(string.digits, k=6))

@app.post("/auth/generate_code")
async def generate_login_code(telegram_id: int = Form(...)):
    """
    Endpoint for the bot to generate a login code for a user.
    """
    # Remove any previous codes for this Telegram user, if they exist.
    codes_to_remove = [code for code, user_id in LOGIN_CODES.items() if user_id == telegram_id]
    for code in codes_to_remove:
        LOGIN_CODES.pop(code, None)

    # Generate and store the new one-time code.
    new_code = generate_code()
    LOGIN_CODES[new_code] = telegram_id
    
    print(f"Código gerado: {new_code} para o telegram_id: {telegram_id}") # Log para debug
    
    return {"status": "success", "code": new_code}

@app.post("/auth/validate_code")
async def validate_login_code(code: str = Form(...)):
    """
    Endpoint for Streamlit to validate a login code.
    """
    # Remove the code from memory so it can only be used once.
    telegram_id = LOGIN_CODES.pop(code, None)

    if telegram_id:
        print(f"Login code {code} validated for telegram_id: {telegram_id}")
        return {"status": "success", "telegram_id": telegram_id}
    else:
        print(f"Login code {code} is invalid or already used.")
        raise HTTPException(status_code=404, detail="Código inválido ou expirado.")
