from pydantic import EmailStr
from sqlmodel import SQLModel, Field,Column,DateTime
from enum import Enum
from datetime import datetime
from typing import Optional


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment_table"

    id: Optional[int] = Field(default=None, primary_key=True)

    content: str
    weight: float = Field(le=25)
    destination: str

    status: ShipmentStatus = Field(default=ShipmentStatus.placed)

    estimated_delivery: Optional[datetime] = Field(
    sa_column=Column(DateTime(timezone=True), nullable=True)
)
    
    
class Seller(SQLModel, table=True):
    id:int= Field(default=None,primary_key=True)
    name:str
    email:EmailStr
    password_hash:str