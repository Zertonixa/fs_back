import logging
import traceback

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger(__name__)


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)

        except Exception as exc:
            log.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())

            return JSONResponse(
                status_code=500, content={"detail": "internal server error", "error": str(exc)}
            )
