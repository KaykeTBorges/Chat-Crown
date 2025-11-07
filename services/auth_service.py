# services/auth_service.py
import hashlib
import hmac
from config import config

class AuthService:
    @staticmethod
    def verify_telegram_auth(data: dict) -> bool:
        """Valida assinatura enviada pelo Telegram OAuth."""
        if "hash" not in data:
            return False

        auth_hash = data.pop("hash")
        secret_key = hashlib.sha256(config.TELEGRAM_BOT_TOKEN.encode()).digest()

        check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

        return computed_hash == auth_hash
