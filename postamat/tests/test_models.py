from django.test import TestCase
from postamat.models import Postamat, Cell, Order
from datetime import datetime, UTC


class ModelTests(TestCase):
    def setUp(self):
        self.postamat = Postamat.objects.create(name='Test', address='123')

    def test_cell_creation(self):
        cell = Cell.objects.create(postamat=self.postamat, number=1)
        self.assertFalse(cell.is_occupied)
        self.assertEqual(str(cell), f"Cell 1 ({self.postamat.name})")

    def test_unique_cell_per_postamat(self):
        Cell.objects.create(postamat=self.postamat, number=1)
        with self.assertRaises(Exception):  # TODO: or IntegrityError?
            Cell.objects.create(postamat=self.postamat, number=1)

    def test_order_creation(self):
        cell = Cell.objects.create(postamat=self.postamat, number=1)
        order = Order.objects.create(
            external_order_id='ORD-1',
            user_phone='+79123456789',
            receive_code='123456',
            postamat=self.postamat,
            cell=cell,
            placed_at=datetime.now(UTC)
        )
        self.assertEqual(order.status, 'placed')
        self.assertIsNotNone(order.receive_code)
