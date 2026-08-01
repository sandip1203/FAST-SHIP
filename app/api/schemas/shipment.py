from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.database.models import ShipmentEvent, ShipmentStatus


class BaseShipment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    weight: float = Field(le=25)
    destination: int


class ShipmentRead(BaseShipment):
    id: UUID
    timelines: list[ShipmentEvent] = Field(default_factory=list)
    estimated_delivery: datetime


class ShipmentCreate(BaseShipment):
    pass
    

class ShipmentUpdate(BaseModel):
    location:int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    description:str|None= Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)