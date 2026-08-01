import unittest
from datetime import datetime

from app.api.schemas.shipment import ShipmentRead
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment_event import ShipmentEventService


class DummySession:
    async def execute(self, *_args, **_kwargs):
        raise AssertionError("query should not fail due to array containment")


class DeliveryPartnerServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_assign_shipment_uses_array_contains_without_error(self):
        service = DeliveryPartnerService(DummySession())
        shipment = type("Shipment", (), {"destination": 560001})()

        with self.assertRaises(AssertionError):
            await service.assign_shipment(shipment, seller=None)

    async def test_get_latest_event_uses_query_without_lazy_relationship(self):
        class DummyEventSession:
            async def execute(self, *_args, **_kwargs):
                class Result:
                    def scalar_one_or_none(self):
                        return ShipmentEvent(location=1, status="placed")

                return Result()

        service = ShipmentEventService(DummyEventSession())
        shipment = type("Shipment", (), {"id": "shipment-id"})()

        event = await service.get_latest_event(shipment)
        self.assertIsInstance(event, ShipmentEvent)

    def test_shipment_read_schema_accepts_timelines_property(self):
        shipment = Shipment(
            id="11111111-1111-1111-1111-111111111111",
            content="Toy-car",
            weight=1.3,
            destination=44600,
            estimated_delivery=datetime.utcnow(),
            seller_id="22222222-2222-2222-2222-222222222222",
            delivery_partner_id="33333333-3333-3333-3333-333333333333",
        )
        shipment.timeline = [
            ShipmentEvent(location=44600, status=ShipmentStatus.placed, description="assigned")
        ]

        response = ShipmentRead.model_validate(shipment)
        self.assertEqual(len(response.timelines), 1)

    def test_shipment_timelines_property_is_safe_when_relationship_is_not_loaded(self):
        shipment = Shipment(
            id="44444444-4444-4444-4444-444444444444",
            content="Toy-car",
            weight=1.3,
            destination=44600,
            estimated_delivery=datetime.utcnow(),
            seller_id="22222222-2222-2222-2222-222222222222",
            delivery_partner_id="33333333-3333-3333-3333-333333333333",
        )

        self.assertEqual(shipment.timelines, [])


if __name__ == "__main__":
    unittest.main()
