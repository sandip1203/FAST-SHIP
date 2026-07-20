from datetime import datetime,timedelta,timezone

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.database.models import Shipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession

class ShipmentServices:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def get(self,id:int)-> Shipment:
        return await self.session.get(Shipment,id)
    
    async def add(self,shipment_create:ShipmentCreate)-> Shipment:
        shipment = Shipment(
        **shipment_create.model_dump(),
        status=ShipmentStatus.placed,
        estimated_delivery = datetime.now(timezone.utc) + timedelta(days=3),
        )

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

     
    async def update(self,id:int,shipment_update:ShipmentUpdate) -> Shipment:
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment
    
    async def delete(self,id:int)->None:
        shipment = await self.get(id)
        await self.session.delete(shipment)
        await self.session.commit()
        return 
        