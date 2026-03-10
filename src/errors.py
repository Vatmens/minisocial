from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class BusinessError(Exception):
    def __init__(
        self,
        message: str,
        error_type: str = "business_error",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        details: dict | None = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}


async def business_error_handler(_: Request, exc: BusinessError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.error_type,
                "message": exc.message,
                "details": exc.details,
            }
        }
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    error_type = "http_error"
    if exc.status_code == 404:
        error_type = "not_found"
    elif exc.status_code == 401:
        error_type = "auth_error"
    elif exc.status_code == 403:
        error_type = "forbidden"
    elif exc.status_code == 409:
        error_type = "conflict"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": error_type,
                "message": str(exc.detail),
                "details": {},
            }
        }
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Invalid input data",
                "details": exc.errors(),
            }
        }
    )


def setup_exception_handlers(app):
    app.add_exception_handler(BusinessError, business_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)