from django.db import models
from django.utils import timezone


class Postamat(models.Model):
    """Postamat model."""
    id = models.BigAutoField(primary_key=True)
    address = models.CharField(max_length=200, verbose_name="Address")
    name = models.CharField(max_length=100, verbose_name="Name")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self):
        return f"{self.name} ({self.address})"


class Cell(models.Model):
    """Postamat cell"""
    postamat = models.ForeignKey(
        Postamat,
        on_delete=models.CASCADE,
        related_name='cells',
        verbose_name="Postamat"
    )
    number = models.PositiveSmallIntegerField(verbose_name="Cell number")
    is_occupied = models.BooleanField(default=False, verbose_name="Occupied")

    class Meta:
        unique_together = ('postamat', 'number')  # the rooms are unique within the postamat
        ordering = ('postamat', 'number')

    def __str__(self):
        return f"Cell {self.number} ({self.postamat.name})"


class Order(models.Model):
    """Order, placed in postamat."""
    STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('received', 'Given'),
        ('failed', 'Placing error'),
    )

    # External order ID from the market (can be a string)
    external_order_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID of order"
    )
    user_phone = models.CharField(max_length=20, verbose_name="User phone number")
    receive_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Receipt code"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='placed',
        verbose_name="Status"
    )
    postamat = models.ForeignKey(
        Postamat,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Postamat"
    )
    cell = models.ForeignKey(
        Cell,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order',
        verbose_name="Cell"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    placed_at = models.DateTimeField(null=True, blank=True, verbose_name="Placed")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="Received")

    def __str__(self):
        return f"Order {self.external_order_id} (cell {self.cell.number if self.cell else '—'})"
