from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import any_, select

from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.database.models import DeliveryPartner, Shipment

from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session):
        super().__init__(DeliveryPartner, session)

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump())

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.serviceable_zip_codes)
                )
            )
        ).all()
    
    async def assign_shipment(self, shipment, seller):
        result = await self.session.execute(
            select(DeliveryPartner)
            .options(
                selectinload(DeliveryPartner.shipments).selectinload(Shipment.timeline)
            )
            .where(
                DeliveryPartner.serviceable_zip_codes.contains([shipment.destination])
            )
        )

        partners = result.scalars().all()

        for partner in partners:
            if partner.current_handling_capacity > 0:
                # assign shipment here
                return partner

        raise HTTPException(status_code=400, detail="No delivery partner available")

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)
