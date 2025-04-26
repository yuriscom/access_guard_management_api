import logging
from typing import Callable

from fastapi import status
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class DetailOutput(BaseModel):
    detail: str = Field(..., description="Message")


class AlreadyExistsException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnknownException(Exception):
    def __init__(self, message = ""):
        self.message = f"Internal Error: {message}"
        super().__init__(self.message)


class UnauthorizedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidFormatException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RequestTimeoutException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BusinessException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ValidationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, e: Exception) -> JSONResponse:
        if isinstance(e, AlreadyExistsException):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(e, InvalidFormatException):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(e, BusinessException):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(e, ValidationException):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(e, NotFoundException):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(e, UnauthorizedException):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(e, UnknownException):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif isinstance(e, RequestTimeoutException):
            status_code = status.HTTP_408_REQUEST_TIMEOUT
        else:
            logger.exception(e)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return JSONResponse(
            status_code=status_code,
            content=DetailOutput(detail=str(e)).model_dump(),
        )
