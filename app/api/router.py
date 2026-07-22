from app.api.routers import shipment,seller
from fastapi import APIRouter

master_router = APIRouter()

master_router.include_router(shipment.router)
master_router.include_router(seller.router)
