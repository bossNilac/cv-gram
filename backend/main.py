import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from backend.routers.auth_routers.auth_router import router as auth_router
from backend.routers.v1.parser import router as parser_v2
from backend.routers.v1.resume_score import router as resume_router
from backend.services.limiter import limiter

ALLOWED_ORIGINS = [
    # Optional: local dev
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = BASE_DIR / "static" / "frontend"

app = FastAPI(title="CV GRAM API", version="0.1.0")



logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def create_app() -> FastAPI:
    # Include routers
    app.include_router(parser_v2, prefix="/parser", tags=["parserV2"])
    app.include_router(resume_router, prefix="/profiles", tags=["parserV2"])
    app.include_router(auth_router, prefix="/auth", tags=["parserV2"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_app()

if FRONTEND_DIST_DIR.exists():
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend_index():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_app(full_path: str):
        if full_path.startswith(("auth", "parser", "profiles", "docs", "redoc", "openapi.json", "assets")):
            raise StarletteHTTPException(status_code=404)

        requested_path = (FRONTEND_DIST_DIR / full_path).resolve()
        try:
            requested_path.relative_to(FRONTEND_DIST_DIR.resolve())
        except ValueError:
            raise StarletteHTTPException(status_code=404)

        if requested_path.is_file():
            return FileResponse(requested_path)

        return FileResponse(FRONTEND_DIST_DIR / "index.html")
