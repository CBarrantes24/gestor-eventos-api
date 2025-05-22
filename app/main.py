from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import example
from app.api import event
from app.api import user
from fastapi import Request, status, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from app.core.auth import verify_jwt  # Importamos la función desde el nuevo módulo

API_PREFIX = "/api/v1"
RATE_LIMIT = 10  # Máximo de requests por minuto por IP

# Simple rate limiter (en memoria, para demo)
rate_limit_cache = {}

def rate_limiter(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = int(time.time() / 60)  # minuto actual
    key = f"{ip}:{now}"
    count = rate_limit_cache.get(key, 0)
    if count >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limit_cache[key] = count + 1

# Middleware para validar headers personalizados (ejemplo)
class HeaderValidatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(f"{API_PREFIX}/") and not request.url.path.endswith("/register") and not request.url.path.endswith("/login"):
            if "X-Client-Header" not in request.headers:
                return JSONResponse(status_code=400, content={"detail": "Missing X-Client-Header"})
        response = await call_next(request)
        return response

app = FastAPI()
app.add_middleware(HeaderValidatorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers con prefijo y dependencias
app.include_router(
    user.router,
    prefix=API_PREFIX
)
app.include_router(
    event.router,
    prefix=API_PREFIX,
    dependencies=[Depends(rate_limiter), Depends(verify_jwt)]
)

