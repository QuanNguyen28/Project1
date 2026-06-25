import uvicorn

from fastapi import FastAPI

import os

import sys

import logging

import time

import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.auth.auth import router as auth_router

from src.api.v1.jd import router as jd_router

from src.api.v1.interview import router as interview_router

from src.api.v1.roles import router as roles_router

from src.api.v1.retriever import router as retrieve_router

from src.api.v1.health import router as health_router

from fastapi.middleware.cors import CORSMiddleware

from src.core.config import CORS_ORIGINS

app = FastAPI(
    title="SmartHire Composer API",
    version="1.0.0",
    description="Assistant for drafting job descriptions and interview questions",
)

logger = logging.getLogger("smarthire.http")


@app.middleware("http")
async def request_observability(request, call_next):

    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    started = time.perf_counter()

    try:

        response = await call_next(request)

    except Exception:

        logger.exception(
            "request_failed method=%s path=%s request_id=%s",
            request.method,
            request.url.path,
            request_id,
        )

        raise

    elapsed_ms = (time.perf_counter() - started) * 1000

    response.headers["X-Request-ID"] = request_id

    response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.1f}"

    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.1f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(jd_router, prefix="")

app.include_router(interview_router, prefix="")

app.include_router(roles_router, prefix="")

app.include_router(retrieve_router, prefix="")

app.include_router(health_router)


@app.get("/ping", tags=["health"])
def ping():

    return {"pong": True}


if __name__ == "__main__":

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
