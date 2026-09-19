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
        labels = {
            "name": "Product Name",
            "sku": " (SKU)",
            "description": "Description",
            "cost_price": "Cost Price",
            "selling_price": "Selling Pricr",
            "stock_quantity" : "Stock Quantity ",
            "min_stock_level": " Min Stock Level",
            "supplier": "Supplier",
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "email", "phone"]
        labels = {
            "name": "Name ",
            "contact_person": "Contact Person ",
            "email": "Email",
            "phone": "Phone",
        }