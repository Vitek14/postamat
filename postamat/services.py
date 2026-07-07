from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Postamat, Cell, Order
from .utils import generate_receive_code
from .notification import NotificationClient
from datetime import datetime, UTC


class PostamatService:
    """Service to work with postamat."""

    def __init__(self, postamat_id: int):
        self.postamat = Postamat.objects.get(id=postamat_id)
        self.notifier = NotificationClient()

    def place_order(self, external_order_id: str, user_phone: str) -> dict:
        """Place order in postamat.

        :returns: Dictionary with cell number and code for opening.
        :rtype: dict
        :raises: ValidationError in error cases(see below)
        """
        if Order.objects.filter(external_order_id=external_order_id).exists():
            raise ValidationError("An order with this ID already exists.")

        # Trying to find empty cell
        free_cell = Cell.objects.select_for_update().filter(
            postamat=self.postamat,
            is_occupied=False
        ).first()
        if not free_cell:
            raise ValidationError("No free cells found in this postamat.")
        free_cell.is_occupied = True
        free_cell.save()

        receive_code = generate_receive_code()
        while Order.objects.filter(receive_code=receive_code).exists():
            receive_code = generate_receive_code()

        with transaction.atomic():
            free_cell.is_occupied = True
            free_cell.save()

            # creating order
            Order.objects.create(
                external_order_id=external_order_id,
                user_phone=user_phone,
                receive_code=receive_code,
                postamat=self.postamat,
                cell=free_cell,
                placed_at=datetime.now(UTC)
            )

        # Sending sms to user
        self.notifier.send_receive_code(user_phone, receive_code, external_order_id)

        return {
            'cell_number': free_cell.number,
            'receive_code': receive_code,
            'order_id': external_order_id,
        }

    def get_order(self, receive_code: str) -> dict:
        """Get order from postamat with receive code. After that, status will change

        :returns: Dictionary about order and cell.
        :rtype: dict
        :raises: ValidationError in error cases(see below)
        """
        try:
            order = Order.objects.select_for_update().get(
                receive_code=receive_code,
                status='placed'
            )
        except Order.DoesNotExist:
            raise ValidationError("Wrong code or order does not exists.")

        # Checking that order is belongs to this postamat.
        if order.postamat != self.postamat:
            raise ValidationError("Order does not belongs to this postamat.")

        cell = order.cell
        with transaction.atomic():
            cell.is_occupied = False
            cell.save()
            order.status = 'received'
            order.received_at = datetime.now(UTC)
            order.save()

        return {
            'order_id': order.external_order_id,
            'cell_number': cell.number,
            'user_phone': order.user_phone,
        }
