from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.database.models import ShipmentStatus


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: str


class ShipmentRead(BaseShipment):
    status: ShipmentStatus
    estimated_delivery: datetime


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    status: Optional[ShipmentStatus] = None
    estimated_delivery: Optional[datetime] = None