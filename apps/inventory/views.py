from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .models import Product

@login_required(login_url='/admin/login/') 
@permission_required('inventory.add_product', raise_exception=True)  
def add_product_view(request):

    return render(request, 'inventory/add_product.html')

@login_required
@permission_required('inventory.view_product', raise_exception=True)
def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})


