"""
Входная точка FastAPI приложения.

- Инициализируйте приложение
- Регистрируйте роутеры и lifespan.
- Запускайте middleware, обработчики исключений и так далее.
"""

from fastapi import FastAPI

from src.api.lifespan import lifespan
from src.apps import api_router  # основной router
from src.core.config import cfg

# from src.core.middleware import setup_middlewares
# from src.core.exceptions import setup_exception_handlers

app = FastAPI(title="My FastAPI App", version="1.0.0", lifespan=lifespan)

# Register API
app.include_router(api_router)

# Опционально: Middleware, Exceptions
# setup_middlewares(app)
# setup_exception_handlers(app)


def main():
    import uvicorn

    uvicorn.run(
        app="src:app",
        host=cfg.app.host,
        port=cfg.app.port,
        reload=cfg.app.reload,
        workers=cfg.app.workers,
    )
