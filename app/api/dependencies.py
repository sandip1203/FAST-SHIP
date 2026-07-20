from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.services.shipment import ShipmentServices

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentServices(session)

ServiceDep = Annotated[ShipmentServices, Depends(get_shipment_service)]