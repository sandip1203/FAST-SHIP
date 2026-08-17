from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.shipment import ShipmentCreate, ShipmentReview, ShipmentUpdate
from app.database.models import (DeliveryPartner, Review, Seller, Shipment,
                                 ShipmentEvent, ShipmentStatus)
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_url_safe_token

from .base import BaseService
from .delivery_partner import DeliveryPartnerService
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

    # Get a shipment by id
    async def get(self, id: UUID) -> Shipment | None:
        # Eager-load timeline to avoid async lazy-loading outside a greenlet
        stmt = select(Shipment).options(selectinload(Shipment.timeline)).where(Shipment.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    def _attach_timeline(self, shipment: Shipment, event: ShipmentEvent | None = None) -> None:
        # Avoid ORM lazy-loading by mutating the underlying dict directly.
        timeline = shipment.__dict__.get("timeline")
        if timeline is None:
            timeline = []
            shipment.__dict__["timeline"] = timeline

        if not isinstance(timeline, list):
            timeline = list(timeline)
            shipment.__dict__["timeline"] = timeline

        if event is not None and event not in timeline:
            timeline.append(event)

    # Add a new shipment
    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now(tz=timezone.utc).replace(tzinfo=None) + timedelta(days=3),
            seller_id=seller.id,
        )
        # Assign delivery partner to the shipment
# ...existing code...
        partner = await self.partner_service.assign_shipment(
            shipment=new_shipment,
            seller=seller,
        )
# ...existing code...
        # Add the delivery partner foreign key
        new_shipment.delivery_partner_id = partner.id
        
        shipment = await self._add(new_shipment)
        
        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name} ",
        )
        self._attach_timeline(shipment, event)
        return shipment

    # Update an existing shipment
    async def update(self,id:UUID,shipment_update:ShipmentUpdate,partner= DeliveryPartner) -> Shipment:
                # Validate logged in parter with assigned partner
        # on the shipment with given id
        shipment = await self.get(id)

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
            )
        update = shipment_update.model_dump(exclude_none=True)
        
        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery
        if len(update)>1 or not shipment_update.estimated_delivery:
            event = await self.event_service.add(
                shipment=shipment,
                **update,
            )
            self._attach_timeline(shipment, event)
        
        return await self._update(shipment)
    
    
    async def rate(self,token:str,review:ShipmentReview):
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized"
            )
        shipment = self.get(UUID(token_data['id']))
        new_review = Review(
            **review.model_dump(),
            shipment_id = shipment.id)
        
        self.session.add(new_review)
        await self.session.commit()
    
    async def cancel (self,id:UUID,seller:Seller)->Shipment:
        ## validate the seller 
        shipment = await self.get(id)
        
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=" Not Authorized"
            )
        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancalled,
        )
        self._attach_timeline(shipment, event)
        return shipment
        
    # Delete a shipment
    async def delete(self, id: int) -> None:
        await self._delete(await self.get(id))
        
        

