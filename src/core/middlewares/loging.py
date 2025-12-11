from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f"[REQ] {request.method} {request.url}")
        response = await call_next(request)
        print(f"[RES] {response.status_code}")
        return response
