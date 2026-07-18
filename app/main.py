import datetime
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from scalar_fastapi import get_scalar_api_reference

from app.database.models import Shipment, ShipmentStatus
from app.database.session import create_db_tables, get_session
from .schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate


# ----------------------------
# App Lifespan
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)


# ----------------------------
# Create Shipment
# ----------------------------
@app.post("/shipments", response_model=ShipmentRead, status_code=201)
def create_shipment(
    payload: ShipmentCreate,
    session: Session = Depends(get_session),
):
    shipment = Shipment(
        **payload.model_dump(),
        status=ShipmentStatus.placed,
        estimated_delivery=datetime.datetime.now() + datetime.timedelta(days=3),
    )

    session.add(shipment)
    session.commit()
    session.refresh(shipment)

    return shipment


# ----------------------------
# Get Shipment by ID
# ----------------------------
@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def get_shipment(
    shipment_id: int,
    session: Session = Depends(get_session),
):
    shipment = session.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    return shipment


# ----------------------------
# Update Shipment
# ----------------------------
@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    payload: ShipmentUpdate,
    session: Session = Depends(get_session),
):
    shipment = session.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    update_data = payload.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update",
        )

    shipment.sqlmodel_update(update_data)

    session.add(shipment)
    session.commit()
    session.refresh(shipment)

    return shipment


# ----------------------------
# Delete Shipment
# ----------------------------
@app.delete("/shipments/{shipment_id}", status_code=200)
def delete_shipment(
    shipment_id: int,
    session: Session = Depends(get_session),
):
    shipment = session.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    session.delete(shipment)
    session.commit()

    return {"detail": f"Shipment {shipment_id} deleted"}


# ----------------------------
# Scalar Docs
# ----------------------------
@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Shipment API Docs",
    )