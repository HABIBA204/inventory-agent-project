from django.contrib import admin
from django.contrib import admin
from .models import Supplier, Product, Purchase, PurchaseItem, Sale, SaleItem

admin.site.register(Supplier)
admin.site.register(Product)


admin.site.register(Purchase)
admin.site.register(PurchaseItem)
admin.site.register(Sale)
admin.site.register(SaleItem)

# Register your models here.
