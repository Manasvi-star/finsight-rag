import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, request_id_var, user_id_var, logger
from backend.app.core.security import decode_access_token
from backend.app.models.database import Base, engine
from backend.app.api.dependencies import limiter

# Import routes
from backend.app.api.routes import auth, ingest, query, analysis, health

# Initialize logging configuration
setup_logging()

# Auto-create tables in development (simple DB migrations)
logger.info("Initializing database and creating schemas...")
Base.metadata.create_all(bind=engine)
logger.info("Database initialized successfully.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup slowapi rate limiting configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configurations for React frontend compatibility (Person B)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware that captures and logs request/response telemetry in structured JSON.
    Tracks Request ID, User ID, and Processing Latency.
    """
    # 1. Generate or extract request ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id_var.set(request_id)

    # 2. Extract user ID if token present
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            user_id_var.set(user_id)

    # 3. Process the request and measure latency
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 4. Emit structured JSON log
    log_extra = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": duration_ms
    }
    logger.info(
        f"HTTP {request.method} {request.url.path} - {response.status_code} ({duration_ms}ms)",
        extra={"extra_info": log_extra}
    )

    response.headers["X-Request-ID"] = request_id
    return response


# Register API routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(ingest.jobs_router)  # /jobs/{job_id}/status
app.include_router(query.router)
app.include_router(analysis.router)
