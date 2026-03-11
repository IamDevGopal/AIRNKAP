from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response

from app.core.exceptions.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

ExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, cast(ExceptionHandler, http_exception_handler))
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(Exception, cast(ExceptionHandler, unhandled_exception_handler))
