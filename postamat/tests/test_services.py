from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from postamat.models import Postamat, Cell, Order
from postamat.services import PostamatService
from postamat.utils import generate_receive_code


class PostamatServiceTests(TestCase):
    def setUp(self):
        self.postamat = Postamat.objects.create(name='Main', address='Main st')
        # Creating 3 cells
        for i in range(1, 4):
            Cell.objects.create(postamat=self.postamat, number=i, is_occupied=False)

    @patch('postamat.services.NotificationClient.send_receive_code')
    def test_place_order_success(self, mock_send):
        service = PostamatService(self.postamat.id)
        result = service.place_order('ORD-1', '+79123456789')
        self.assertEqual(result['order_id'], 'ORD-1')
        self.assertIn('cell_number', result)
        self.assertIn('receive_code', result)

        cell = Cell.objects.get(postamat=self.postamat, number=result['cell_number'])
        self.assertTrue(cell.is_occupied)  # cell must be occupied

        order = Order.objects.get(external_order_id='ORD-1')
        self.assertEqual(order.status, 'placed')
        self.assertEqual(order.cell, cell)
        mock_send.assert_called_once_with(
            '+79123456789',
            order.receive_code,
            'ORD-1'
        )

    def test_place_order_no_free_cells(self):
        Cell.objects.update(is_occupied=True)
        service = PostamatService(self.postamat.id)
        with self.assertRaises(ValidationError) as cm:
            service.place_order('ORD-2', '+79123456789')
        self.assertIn('No free cells found in this postamat.', str(cm.exception))

    def test_place_order_duplicate(self):
        service = PostamatService(self.postamat.id)
        service.place_order('ORD-3', '+79123456789')
        with self.assertRaises(ValidationError) as cm:
            service.place_order('ORD-3', '+79123456789')
        self.assertIn('already exists', str(cm.exception))

    def test_get_order_success(self):
        service = PostamatService(self.postamat.id)
        result = service.place_order('ORD-4', '+79123456789')
        receive_code = result['receive_code']
        cell_number = result['cell_number']

        get_result = service.get_order(receive_code)
        self.assertEqual(get_result['order_id'], 'ORD-4')
        self.assertEqual(get_result['cell_number'], cell_number)
        cell = Cell.objects.get(postamat=self.postamat, number=cell_number)
        self.assertFalse(cell.is_occupied)
        order = Order.objects.get(external_order_id='ORD-4')
        self.assertEqual(order.status, 'received')

    def test_get_order_invalid_code(self):
        service = PostamatService(self.postamat.id)
        with self.assertRaises(ValidationError) as cm:
            service.get_order('000000')
        self.assertIn('Wrong code or order does not exists.', str(cm.exception))

    def test_get_order_already_received(self):
        service = PostamatService(self.postamat.id)
        result = service.place_order('ORD-5', '+79123456789')
        receive_code = result['receive_code']
        service.get_order(receive_code)
        with self.assertRaises(ValidationError) as cm:
            service.get_order(receive_code)
        self.assertIn('Wrong code or order does not exists.', str(cm.exception))
