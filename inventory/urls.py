from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('owner-login/', views.owner_login, name='owner_login'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('stock-available/', views.stock_available, name='stock_available'),
    path('low-stock-alert/', views.low_stock_alert, name='low_stock_alert'),
    path('sales-details/', views.sales_details, name='sales_details'),
    path('total-sales/', views.total_sales, name='total_sales'),
    path('highest-sold-products/', views.highest_sold_products, name='highest_sold_products'),
    path('add-to-basket/', views.add_to_basket, name='add_to_basket'),
    path('checkout/', views.checkout, name='checkout'),
] 