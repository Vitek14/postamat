from django.urls import path
from . import views

app_name = 'postamat'

urlpatterns = [
    path('api/postamat/<int:postamat_id>/place/', views.place_order, name='place_order'),
    path('api/postamat/<int:postamat_id>/get/', views.get_order, name='get_order'),
    # UI pages
    path('', views.index, name='index'),
    path('postamat/<int:postamat_id>/place/', views.place_order_ui, name='place_order_ui'),
    path('postamat/<int:postamat_id>/get/', views.get_order_ui, name='get_order_ui')
]
