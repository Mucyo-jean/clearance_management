"""Application error types and the single handler that formats them.

Every failure leaves the API in the same shape:

    {"success": false, "message": "...", "details": null}

Defining it once here is what stops individual endpoints inventing their own
error formats, which is what makes the frontend able to show a useful message
for any failure without special-casing each endpoint.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base class for errors this application raises deliberately."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Something went wrong"

    def __init__(self, message: str | None = None, details: object | None = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class ConflictError(AppError):
    """The request is valid but clashes with current state (e.g. Rule R1)."""

    status_code = status.HTTP_409_CONFLICT
    message = "Request conflicts with the current state"


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Not authenticated"


class ForbiddenError(AppError):
    """Authenticated, but not allowed to touch this particular resource."""

    status_code = status.HTTP_403_FORBIDDEN
    message = "You do not have permission to perform this action"


class ValidationError(AppError):
    # Numeric literal rather than status.HTTP_422_*: Starlette renamed the
    # constant from _UNPROCESSABLE_ENTITY to _UNPROCESSABLE_CONTENT in 1.6,
    # so the literal keeps this working across both.
    status_code = 422
    message = "The submitted data is not valid"


def _payload(message: str, details: object | None = None) -> dict:
    return {"success": False, "message": message, "details": details}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the handlers. Called once from the app factory."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(exc.message, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Reshape FastAPI's default 422 into "field: message" pairs the
        # frontend can show next to the offending input.
        fields = [
            {
                "field": ".".join(str(p) for p in err["loc"] if p != "body"),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_payload("The submitted data is not valid", fields),
        )
