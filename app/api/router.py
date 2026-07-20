from fastapi import APIRouter,Depends,HTTPException,status
from app.api.dependencies import ServiceDep
from app.database.models import Shipment, ShipmentStatus
from app.database.session import create_db_tables, SessionDep
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from sqlalchemy.orm import Session

from app.services.shipment import ShipmentServices

router = APIRouter(
    prefix='/shipment',
    tags=['Shipment'],
    dependencies=[ServiceDep]
)


@router.post("/shipments", response_model=ShipmentRead)
async def create_shipment(
    shipment: ShipmentCreate,
    service: ServiceDep
):
    return await service.add(shipment)


@router.get("/shipments/{shipment_id}", response_model=ShipmentRead)
async def get_shipment(
    shipment_id: int,
    service: ServiceDep
):
    shipment = await service.get(shipment_id)

    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return shipment


@router.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
async def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    service: ServiceDep,
):
    update_data = shipment_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided")

    return await service.update(shipment_id, update_data)


@router.delete("/shipments/{shipment_id}")
async def delete_shipment(
    shipment_id: int,
    service: ServiceDep,
):
    await service.delete(shipment_id)
    return {"detail": f"shipment #{shipment_id} deleted"}

