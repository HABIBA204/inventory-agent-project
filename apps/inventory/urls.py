from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # الرئيسية
    path('products/', views.product_list_view, name='product_list'),  # قائمة المنتجات
    path('products/add/', views.add_product_view, name='add_product'),  # إضافة منتج
    path('products/<int:pk>/edit/', views.edit_product_view, name='edit_product'),  # تعديل منتج
    path('products/<int:pk>/delete/', views.delete_product_view, name='delete_product'),  # حذف منتج
    path('suppliers/', views.supplier_list_view, name='supplier_list'),  # الموردين
    path('reports/', views.reports_view, name='reports'),  # التقارير
]