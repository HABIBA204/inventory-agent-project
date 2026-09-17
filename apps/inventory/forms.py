from django import forms

from .models import Product, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "min_stock_level",
            "supplier",
        ]


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "email", "phone"]