from django.contrib import admin
from .models import Postamat, Cell, Order


@admin.register(Postamat)
class PostamatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'is_active')


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('postamat', 'number', 'is_occupied')
    list_filter = ('postamat', 'is_occupied')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('external_order_id', 'user_phone', 'receive_code', 'status', 'placed_at')
    list_filter = ('status', 'postamat')
    search_fields = ('external_order_id', 'receive_code', 'user_phone')
