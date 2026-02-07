import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    mail_host: str = os.getenv("MAIL_HOST", "smtp.gmail.com")
    mail_port: int = int(os.getenv("MAIL_PORT", "587"))
    mail_username: str = os.getenv("MAIL_USERNAME", "")
    mail_password: str = os.getenv("MAIL_PASSWORD", "")
    mail_from: str = os.getenv("MAIL_FROM", "CVGram <no-reply@cvgram.local>")

    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    support_email: str = os.getenv("SUPPORT_EMAIL", "support@cvgram.local")

settings = Settings()
