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

    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_adv_api_key = os.getenv("OPENAI_ADV_API_KEY", "")

    cv_max_mb = float(os.getenv("CV_MAX_MB", "10"))
    chunk = 1 * 1024 * 1024  # 1 MB

    primary_model = os.getenv("PRIMARY_MODEL", "gpt-4o-mini")
    escalation_model = os.getenv("ESCALATION_MODEL", "gpt-4o")
    adv_model = os.getenv("ADV_MODEL", "gpt-5-mini-2025-08-07")

    auto_escalate = os.getenv("AUTO_ESCALATE", "1") == "1"
    min_confidence = float(os.getenv("MIN_CONFIDENCE", "0.50"))


settings = Settings()
