from fastapi import FastAPI

import logging

from routers.v1.resume_score import router as resume_router
from routers.v1.parser import router as parser_v2
from routers.auth_routers.auth_router import router as auth_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

ALLOWED_ORIGINS = [
    # Optional: local dev
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app = FastAPI(title="CV GRAM API", version="0.1.0")



logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def create_app() -> FastAPI:
    # Include routers
    app.include_router(parser_v2, prefix="/parser", tags=["parserV2"])
    app.include_router(resume_router, prefix="/profile", tags=["parserV2"])
    app.include_router(auth_router, prefix="/auth", tags=["parserV2"])

    return app

app = create_app()