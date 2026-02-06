import os

from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

import logging

from sqlalchemy import text

from models.user_challenge import UserChallenge
from routers.v1.challenges import today_utc
from sqlalchemy.orm import Session
from db import SessionLocal  # your session factory
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers.v1 import tasks, preferences, xp, challenges, resume_score
from routers.v2 import parser as parser_v2
from routers.v2 import pre_sign_up_parser as pre_parser
from security import auth_middleware
from security.ip_tracker_limiter_for_pre import IPRateLimitMiddleware

ALLOWED_ORIGINS = [
    "https://elite-score-frontend-e37a4c9b861e.herokuapp.com",
    "https://www.elite-score.com",
    # Optional: local dev
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]




app = FastAPI(title="Challenge Verification API", version="0.1.0")



logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

scheduler = AsyncIOScheduler(timezone="UTC")
def disable_challenges():
    logging.info("Expiration Job Activated")
    db: Session = SessionLocal()
    try:
        updated = (
            db.query(UserChallenge)
              .filter(
                  UserChallenge.due_at < today_utc(),                     # your helper returns UTC
                  UserChallenge.status.in_(["assigned", "started"])
              )
              .update({"status": "expired"}, synchronize_session=False)
        )
        db.commit()
        logging.info("Expiration Job: updated %d rows", updated)
    except Exception:
        logging.exception("Expiration Job failed")
    finally:
        db.close()

def finalize_all_user_streaks_for_yesterday():
    logging.info("Streaks Job Activated")
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT challenges_schema.finalize_all_user_streaks_for_yesterday()"))
        db.commit()
    except Exception:
        logging.exception("Streaks Job failed")
    finally:
        db.close()


@app.on_event("startup")
def _startup():
    """
    Startup event handler
    """
    scheduler.add_job(disable_challenges, CronTrigger(hour=00, minute=15))
    scheduler.add_job(finalize_all_user_streaks_for_yesterday, CronTrigger(hour=00, minute=30))
    # For testing: fire every minute
    scheduler.start()
    logging.info("Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown(wait=False)
    logging.info("Scheduler stopped")


def create_app() -> FastAPI:

    # Include middleware
    app.add_middleware(auth_middleware.AuthCORSFilterMiddleware) #,allow_origins=ALLOWED_ORIGINS)

    app.add_middleware(
        IPRateLimitMiddleware,
        limit=2,  # 2 requests
        window_sec=60,  # per 60 seconds
        block_sec=600,  # then block for 10 minutes
        paths={"/v2/parser/resume/score","/v2/parser/resume/cv","/v2/parser/resume/store/score"},
    )

    # Include routers
    app.include_router(parser_v2.router, prefix="/v2/parser", tags=["parserV2"])
    app.include_router(pre_parser.router, prefix="/v2/pre-parser", tags=["parserV2"])
    app.include_router(challenges.router, prefix="/v1/challenges", tags=["challenges"])
    app.include_router(resume_score.router, prefix="/v1/users", tags=["resume"])
    app.include_router(preferences.router, prefix="/v1/preferences", tags=["preferences"])
    app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
    app.include_router(xp.router, prefix="/v1/xp", tags=["xp"])

    return app

app = create_app()