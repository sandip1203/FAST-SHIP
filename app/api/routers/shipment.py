from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils import TEMPLATE_DIR

from ..dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep
from ..schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentReview, ShipmentUpdate


router = APIRouter(prefix="/shipment", tags=["Shipment"])

templates= Jinja2Templates(TEMPLATE_DIR)

## Tracking details of Shipment 
@router.get("/track")
async def get_tracking(request:Request ,id:UUID,service:ShipmentServiceDep):
    ## check for shipment with given id 
    shipment = await service.get(id)
    context = shipment.model_dump()
    
    context['status'] = shipment.status
    context["partner"] = shipment.delivery_partner.name
    context['timeline']= shipment.timeline
    
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context
    )




### Read a shipment by id
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ShipmentServiceDep):
    # Check for shipment with given id
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipment

### Create a new shipment
@router.post("/", response_model=ShipmentRead)
async def submit_shipment(
    seller: SellerDep,
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
):
    return await service.add(shipment, seller)


### Update fields of a shipment
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,
    service: ShipmentServiceDep,
):
    # Update data with given fields
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )
    
    return await service.update(id,shipment_update,partner)


### Delete a shipment by id
@router.get("/cancel",response_model=ShipmentRead)
async def cancel_shipment(id: UUID,seller:SellerDep, service: ShipmentServiceDep) -> dict[str, str]:
    # Remove from database
    await service.cancel(id,seller)

    return {"detail": f"Shipment with id #{id} is cancelled!"}



### submit a review for a shipment 
@router.post("/review")
async def submit_review(
    token:str,
    review: ShipmentReview,
    service: ShipmentServiceDep
):
    await service.rate(token,review)
    return {"detail":"Review submitted"}