from fastapi import FastAPI

from src.api.lifespan import lifespan
from src.apps import api_router
from src.apps.health import health_router
from src.apps.seo import seo_router
from src.core.config import cfg
from src.core.middlewares import setup_middlewares

app = FastAPI(title="My FastAPI App", version="1.0.0", lifespan=lifespan)

app.include_router(health_router)
app.include_router(seo_router)
app.include_router(api_router)

setup_middlewares(app)


def main():
    import uvicorn

    uvicorn.run(
        app="src.api.main:app",
        host=cfg.app.host,
        port=cfg.app.port,
        reload=cfg.app.reload,
        workers=cfg.app.workers,
    )
