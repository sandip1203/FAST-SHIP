from fastapi import APIRouter
from .routers import shipment
from .routers import delivery_partner
from .routers import seller

# Single router to group all api routers
master_router = APIRouter()

master_router.include_router(shipment.router)
master_router.include_router(seller.router)
master_router.include_router(delivery_partner.router)