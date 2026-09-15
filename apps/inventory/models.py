from django.conf import settings
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)
    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Stock:{self.stock_quantity})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level


class Purchase(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_ORDERED = "ordered"
    STATUS_RECEIVED = "received"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending Approval"),
        (STATUS_ORDERED, "Ordered"),
        (STATUS_RECEIVED, "Received"),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="purchases")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchases_created",
    )
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_create_draft_po", "Can create draft purchase orders via AI agent"),
        ]

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "Unknown"
        return f"Purchase #{self.id} - {supplier_name} ({self.status})"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="item")
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="purchase_item")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Sale(models.Model):
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.id} - Total: {self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Sold)"
    