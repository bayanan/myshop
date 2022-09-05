from . import views
from django.urls import path
from django.utils.translation import gettext_lazy as _

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('admin/orders/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/order/<int:order_id>/pdf/', views.admin_order_pdf, name='admin_order_pdf'),
]
