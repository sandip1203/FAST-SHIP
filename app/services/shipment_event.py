from sqlmodel import select

from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService):
    def __init__(self,session,tasks):
        super().__init__(ShipmentEvent,session)
        self.notification_service = NotificationService(tasks)
        
    async def add(
        self,
        shipment: Shipment,
        location: int = None,
        status: ShipmentStatus = None,
        description: str = None,
    ) -> ShipmentEvent:
        if location is None or status is None:
            try:
                last_event = await self.get_latest_event(shipment)
            except ValueError:
                if location is None:
                    location = 0
                if status is None:
                    status = ShipmentStatus.placed
            else:
                location = location if location is not None else last_event.location
                status = status if status is not None else last_event.status

        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=description if description is not None else self._generate_description(status, location),
            shipment_id=shipment.id,
        )
        await self._notify(shipment,status)
        return await self._add(new_event)
    
    async def get_latest_event(self, shipment: Shipment):
        result = await self.session.execute(
            select(ShipmentEvent)
            .where(ShipmentEvent.shipment_id == shipment.id)
            .order_by(ShipmentEvent.created_at.desc())
            .limit(1)
        )
        last_event = result.scalar_one_or_none()
        if last_event is None:
            raise ValueError("No shipment events found")
        return last_event

    def _generate_description(self,status:ShipmentStatus,location:int):
        match status:
            case ShipmentStatus.placed:
                return " assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return " Shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return " cancelled by seller"
            case _:
                return f"scanned at {location} "
            
            
    async def _notify(self,shipment:Shipment,status:ShipmentStatus):
        if status== ShipmentStatus.in_transit:
            return 
        subject:str
        context={}
        template_name:str
        
        
        match status:
            case ShipmentStatus.placed:
                        subject="your order is shipped"
                        context["id"]= shipment.id
                        context["seller"]=shipment.seller.name
                        context["partner"]=shipment.delivery_partner.name
                        template_name="mail_placed.html"

            case ShipmentStatus.out_for_delivery:
                subject="your order is arriving soon"
                template_name="mail_out_for_delivery.html"
            case ShipmentStatus.delivered:
                            subject="your order is Delivered"
                            template_name="mail_delivered.html"
            case ShipmentStatus.cancelled:
                            subject="your order is cancelled"
                            template_name="mail_cancelled.html"
                
        self.notification_service.send_email_with_template(
            recipients=[shipment.client_contact_email],
            subject = subject,
            context=context,
            template_name=template_name
        )          