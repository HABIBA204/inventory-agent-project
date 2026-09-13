from django.db import models

class Supplier(models.Model):
    name=models.CharField(max_length=255,unique=True)
    contact_person=models.CharField(max_length=255,blank=True, null=True)
    email=models.EmailField(blank=True, null=True)
    phone=models.CharField(max_length=50, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    name=models.CharField(max_length=255)
    sku=models.CharField(max_length=100, unique=True)
    description=models.TextField(blank=True,null=True)
    cost_price=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity=models.IntegerField(default=0)
    min_stock_level=models.IntegerField(default=5)
    supplier=models.ForeignKey('Supplier', on_delete=models.SET_NULL,
                                   null=True,blank=True,related_name='products')
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Stock:{self.stock_quantity})"

        

class Purchase(models.Model):
    supplier=models.ForeignKey(Supplier,on_delete=models.SET_NULL, null=True, related_name='purchases' )
    total_cost=models.DecimalField(max_digits=12,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"purchase #{self.id} - {self.supplier.name if self.supplier else 'Unknown'}"

class PurchaseItem(models.Model):
    purchase=models.ForeignKey(Purchase ,on_delete=models.CASCADE,related_name='item')
    quantity=models.IntegerField()
    unit_cost=models.DecimalField(max_digits=10, decimal_places=2)
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='purchase_item')
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Sale(models.Model):
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.id} - Total: {self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Sold)"

        



        

# Create your models here.

