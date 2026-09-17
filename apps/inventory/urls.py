from django.urls import path

from .views import product_list_view, add_product_view

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'), # الرئيسية
    path('products/', views.product_list_view, name='product_list'), # قائمة المنتجات
    path('products/add/', views.add_product_view, name='add_product'), # إضافة منتج
    path('suppliers/', views.supplier_list_view, name='supplier_list'), # الموردين
    path('reports/', views.reports_view, name='reports'), # التقارير
]