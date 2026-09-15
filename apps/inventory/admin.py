from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import Supplier, Product, Purchase, PurchaseItem, Sale, SaleItem

def setup_default_groups():
    try:
        owner_group, _ = Group.objects.get_or_create(name='Owner')
        all_permissions = Permission.objects.filter(content_type__app_label='inventory')
        owner_group.permissions.set(all_permissions)

        employee_group, _ = Group.objects.get_or_create(name='Employee')
        employee_permissions = Permission.objects.filter(
            content_type__app_label='inventory',
            codename__in=[
                'view_supplier', 'add_supplier',
                'view_product', 'add_product', 'change_product',
                'view_purchase', 'add_purchase',
                'view_purchaseitem', 'add_purchaseitem',
                'view_sale', 'add_sale',
                'view_saleitem', 'add_saleitem',
            ]
        )
        employee_group.permissions.set(employee_permissions)
    except Exception:
        pass

setup_default_groups()

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'selling_price', 'stock_quantity', 'is_low_stock')
    search_fields = ('name', 'sku')
    list_filter = ('supplier', 'update_at')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'total_cost', 'created_at')
    list_filter = ('status', 'supplier', 'created_at')

@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'product', 'quantity', 'unit_cost')
    search_fields = ('product__name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_amount', 'created_at')
    list_filter = ('created_at',)

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price')
    search_fields = ('product__name',)

