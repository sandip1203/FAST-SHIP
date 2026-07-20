from contextlib import asynccontextmanager
from app.database.session import create_db_tables
from fastapi import FastAPI
from app.api.router import router
from scalar_fastapi import get_scalar_api_reference



# ----------------------------
# App Lifespan
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)



# ----------------------------
# Scalar Docs
# ----------------------------
@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Shipment API Docs",
    )