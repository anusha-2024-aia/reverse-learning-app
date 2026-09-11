from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppException, ErrorCode
from app.core.logging_config import logger

STATUS_CODE_TO_ERROR_CODE = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.AUTHENTICATION_FAILED,
    403: ErrorCode.AUTHORIZATION_FAILED,
    404: ErrorCode.RESOURCE_NOT_FOUND,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMIT_EXCEEDED,
    500: ErrorCode.INTERNAL_SERVER_ERROR,
    503: ErrorCode.AI_SERVICE_ERROR,
}

def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = get_request_id(request)
    logger.warning(f"[{request_id}] Handled AppException ({exc.status_code} {exc.error_code}): {exc.message}")
    
    content = {
        "success": False,
        "error": exc.error_code,
        "message": exc.message,
    }
    if exc.details is not None:
        content["details"] = exc.details
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    error_code = STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    safe_message = str(exc.detail) if isinstance(exc.detail, str) else "Request error occurred."
    logger.warning(f"[{request_id}] HTTPException ({exc.status_code} {error_code}): {safe_message}")

    content = {
        "success": False,
        "error": error_code,
        "message": safe_message,
    }
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = get_request_id(request)
    logger.warning(f"[{request_id}] RequestValidationError on {request.method} {request.url.path}")

    # Build safe clean detail messages without exposing sensitive internals
    clean_details = []
    for err in exc.errors():
        loc = [str(x) for x in err.get("loc", []) if x not in ("body", "query", "path")]
        clean_details.append({
            "field": ".".join(loc) if loc else "payload",
            "message": err.get("msg", "Invalid input value")
        })

    content = {
        "success": False,
        "error": ErrorCode.VALIDATION_ERROR,
        "message": "The request contains invalid data.",
        "details": clean_details,
    }
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    request_id = get_request_id(request)
    logger.error(f"[{request_id}] Database operation error: {type(exc).__name__}")

    content = {
        "success": False,
        "error": ErrorCode.DATABASE_ERROR,
        "message": "Unable to complete database operation right now.",
    }
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

async def global_unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    logger.exception(f"[{request_id}] Unhandled unexpected exception on {request.method} {request.url.path}: {exc}")

    content = {
        "success": False,
        "error": ErrorCode.INTERNAL_SERVER_ERROR,
        "message": "An unexpected error occurred. Please try again later.",
    }
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, global_unexpected_exception_handler)
