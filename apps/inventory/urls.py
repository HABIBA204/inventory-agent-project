from django.urls import path

from .views import product_list_view, add_product_view

urlpatterns = [
    # رابط صفحة قائمة المنتجات
    path('products/', product_list_view, name='product_list'),
    
    # رابط صفحة إضافة منتج
    path('products/add/', add_product_view, name='add_product'),
]