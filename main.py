import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes.upload import router as upload_router
from utils.errors import APIError, build_error_response

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("resume_parser")


def _get_allowed_origins() -> list[str]:
    """Parse comma-separated CORS origins from the environment."""
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


app = FastAPI(
    title="AI Resume Parser API",
    description="Upload resumes and extract structured resume data from PDF and DOCX files.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request method, path, status code, and duration."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(APIError)
async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    """Return a normalized API error payload."""
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return a normalized payload for request validation errors."""
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg", "Invalid request.")
    return build_error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message=message,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Normalize framework-raised HTTP errors."""
    return build_error_response(
        status_code=exc.status_code,
        code="VALIDATION_ERROR",
        message=str(exc.detail),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return a safe response for unexpected server errors."""
    logger.exception("Unhandled server error: %s", exc)
    return build_error_response(
        status_code=500,
        code="PARSE_FAILED",
        message="An unexpected error occurred while processing the request.",
    )


app.include_router(upload_router)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Return API health and version information."""
    return {"status": "ok", "version": "1.0.0"}
