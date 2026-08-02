from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
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


app = FastAPI(
    title="FAST-SHIP",
    version="1.0.0",
    lifespan=lifespan_handler,
)

app.include_router(master_router)

@app.get("/mail")
async def send_test_mail(tasks:BackgroundTasks):
    tasks.add_task(
        NotificationService().send_email,
        recipients = ["mahatsanjip3@gmail.com"],
        subject = "Test mail coming through once",
        body = "you shouldn;t be interested in every body ...",
    )
    return {"detail":"mail sending......."}




@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )