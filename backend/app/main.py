# backend/app/main.py
import logging
import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware



# configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("voiture-search")

# import routers
from app.routes import vehicles, search, auth, alerts, search_history, chatbot, similar, admin, scrape, search_advanced, assisted, messages, pro  # noqa: E402
from app.routes.favorites import router as favorites_router  # noqa: E402

app = FastAPI(title="Voiture Search API", version="0.2.0")


# CORS - allow frontend local and production origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

allow_origins_env = os.getenv("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
if allow_origins_env.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# basic request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"-> {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.debug(f"<- {request.method} {request.url} {response.status_code}")
            return response
        except Exception as exc:
            logger.exception("Unhandled exception in request pipeline")
            raise

app.add_middleware(RequestLoggingMiddleware)

# include routers
app.include_router(vehicles.router)
app.include_router(search.router)
app.include_router(search_advanced.router)
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(search_history.router)
app.include_router(favorites_router)
app.include_router(chatbot.router)
app.include_router(similar.router)
app.include_router(admin.router)
app.include_router(scrape.router)
app.include_router(assisted.router)
app.include_router(messages.router)
app.include_router(pro.router)

# Exception handlers for nicer JSON errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "detail": exc.errors()},
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    logger.warning("Pydantic validation error: %s", exc.errors())
    return JSONResponse(status_code=422, content={"error": "validation_error", "detail": exc.errors()})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "detail": "An internal error occurred."})

@app.get("/")
async def root():
    return {"message": "API ok", "version": "0.2.0"}