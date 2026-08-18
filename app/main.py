import logging
from contextlib import asynccontextmanager
from time import perf_counter

from cryptography.fernet import InvalidToken
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.core.exceptations import add_exception_handlers
from app.database.session import create_db_tables
from app.services.notification import NotificationService

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    app.state.db_ready = True
    try:
        yield
    finally:
        app.state.db_ready = False


logger = logging.getLogger("fastship")

app = FastAPI(
    title="FAST-SHIP",
    version="1.0.0",
    lifespan=lifespan_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)
app.include_router(master_router)


@app.exception_handler(InvalidToken)

async def invalid_token_handler(request: Request, exc: InvalidToken):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid token"}
    )

@app.get("/mail")
async def send_test_mail(tasks:BackgroundTasks):
    tasks.add_task(
        NotificationService().send_email,
        recipients = ["mahatsanjip3@gmail.com"],
        subject = "Test mail coming through once",
        body = "you shouldn;t be interested in every body ...",
    )
    return {"detail":"mail sending......."}

def add_log(message: str):
    logger.info(message)


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start

    add_log(
        f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}s)"
    )
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )