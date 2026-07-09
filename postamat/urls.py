from django.urls import path
from . import views

app_name = 'postamat'

urlpatterns = [
    path('admin/login/', views.admin_login_redirect),
    path('api/postamat/<int:postamat_id>/place/', views.place_order, name='place_order'),
    path('api/postamat/<int:postamat_id>/get/', views.get_order, name='get_order'),
    # UI pages
    path('', views.index, name='index'),
    path('postamat/<int:postamat_id>/place/', views.place_order_ui, name='place_order_ui'),
    path('postamat/<int:postamat_id>/get/', views.get_order_ui, name='get_order_ui'),

    path('verify-code/<str:postamat_id>/', views.verify_code, name='verify_code'),
    path('register-for-order/<str:postamat_id>/', views.register_for_order, name='register_for_order'),
]
