from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from .forms import ProductForm, SupplierForm
from .models import Product, Supplier
from .services import auto_generate_draft_orders, get_open_draft_orders


@login_required(login_url='/admin/login/')
@permission_required('inventory.add_product', raise_exception=True)
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form})


@login_required
@permission_required('inventory.view_product', raise_exception=True)
def product_list_view(request):
    # كشف تلقائي: لو أي منتج قل عن الحد الأدنى، يتجهزله مسودة طلب شراء من غير ما حد يطلب
    auto_created_orders = auto_generate_draft_orders()

    products = Product.objects.all().select_related('supplier')
    return render(
        request,
        'inventory/product_list.html',
        {'products': products, 'auto_created_orders': auto_created_orders},
    )


@login_required
def dashboard_view(request):
    auto_created_orders = auto_generate_draft_orders()
    return render(
        request,
        'inventory/dashboard.html',
        {'auto_created_orders': auto_created_orders},
    )


@login_required
@permission_required('inventory.view_supplier', raise_exception=True)
def supplier_list_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    suppliers = Supplier.objects.all().order_by('name')
    return render(
        request,
        'inventory/supplier_list.html',
        {'suppliers': suppliers, 'form': form},
    )


@login_required
def reports_view(request):
    products = Product.objects.all()
    low_stock_products = [p for p in products if p.is_low_stock]

    context = {
        'total_products': products.count(),
        'total_suppliers': Supplier.objects.count(),
        'low_stock_products': low_stock_products,
        'low_stock_count': len(low_stock_products),
        'draft_orders': get_open_draft_orders(),
    }
    return render(request, 'inventory/reports.html', context)