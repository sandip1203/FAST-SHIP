from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.database.session import create_db_tables


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


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )