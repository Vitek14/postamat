from django.urls import path
from . import views

app_name = 'postamat'

urlpatterns = [
    path('postamat/<int:postamat_id>/place/', views.place_order, name='place_order'),
    path('postamat/<int:postamat_id>/get/', views.get_order, name='get_order'),
]
