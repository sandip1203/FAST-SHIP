from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import INTEGER
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=utc_now,
        )
    )

    content: str
    weight: float = Field(le=25)
    destination: int
    estimated_delivery: datetime
    timeline:list["ShipmentEvent"]= Relationship(
        back_populates="shipment"
    )
    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    delivery_partner_id: UUID = Field(
        foreign_key="delivery_partner.id",
    )
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    
    @property
    def status(self):
        timeline = self.__dict__.get("timeline")
        return timeline[-1].status if timeline else None

    @property
    def timelines(self) -> list["ShipmentEvent"]:
        timeline = self.__dict__.get("timeline")
        if timeline is None:
            return []
        return list(timeline)

    @timelines.setter
    def timelines(self, value: list["ShipmentEvent"]):
        self.timeline = value

class ShipmentEvent(SQLModel,table=True):
    __tablename__="shipment_event"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=utc_now,
        )
    )
    location:int
    status:ShipmentStatus
    description:str | None = Field(default=None)
    
    shipment_id:UUID = Field(foreign_key="shipment.id")
    shipment:Shipment= Relationship(
        back_populates="timeline",
        sa_relationship_kwargs={"lazy":"selectin"}
    )
    
    

class User(SQLModel):
    name: str

    email: EmailStr
    password_hash: str = Field(exclude=True)


class Seller(User, table=True):
    __tablename__ = "seller"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=utc_now,
        )
    )
    address:str | None= Field(default=None)
    zip_code:int | None= Field(default=None)

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=utc_now,
        )
    )

    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(postgresql.ARRAY(INTEGER)),
    )
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    
    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered 
            or shipment.status != ShipmentStatus.cancelled
        ]
    
    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)
