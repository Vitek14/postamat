from django.test import TestCase, Client
from django.urls import reverse
from postamat.models import Postamat, Cell


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.postamat = Postamat.objects.create(name='Test', address='Addr')

        Cell.objects.create(postamat=self.postamat, number=1, is_occupied=False)
        Cell.objects.create(postamat=self.postamat, number=2, is_occupied=False)

    def test_place_order_endpoint_success(self):
        url = reverse('postamat:place_order', kwargs={'postamat_id': self.postamat.id})
        data = {'order_id': 'V-1', 'user_phone': '+79123456789'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('cell_number', json_data)
        self.assertIn('receive_code', json_data)
        self.assertEqual(json_data['order_id'], 'V-1')

    def test_place_order_no_json(self):
        url = reverse('postamat:place_order', kwargs={'postamat_id': self.postamat.id})
        response = self.client.post(url, {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing', response.json()['error'])

    def test_place_order_missing_field(self):
        url = reverse('postamat:place_order', kwargs={'postamat_id': self.postamat.id})
        data = {'order_id': 'V-2'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing', response.json()['error'])

    def test_get_order_endpoint_success(self):
        from postamat.services import PostamatService
        service = PostamatService(self.postamat.id)
        result = service.place_order('V-3', '+79123456789')
        receive_code = result['receive_code']

        url = reverse('postamat:get_order', kwargs={'postamat_id': self.postamat.id})
        response = self.client.post(url, {'receive_code': receive_code}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['order_id'], 'V-3')
        self.assertEqual(response.json()['cell_number'], result['cell_number'])

    def test_get_order_invalid_code(self):
        url = reverse('postamat:get_order', kwargs={'postamat_id': self.postamat.id})
        response = self.client.post(url, {'receive_code': '000000'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Wrong code or order does not exists.', response.json()['error'])
