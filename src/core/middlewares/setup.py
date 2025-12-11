from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .error import ErrorMiddleware
from .loging import LoggingMiddleware


def setup_middlewares(app: FastAPI) -> None:

    app.add_middleware(ErrorMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
