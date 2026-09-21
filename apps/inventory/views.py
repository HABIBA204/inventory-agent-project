from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect

from .forms import ProductForm, SupplierForm
from .models import Product, Purchase, Sale, Supplier
from .services import auto_generate_draft_orders, get_low_stock_products, get_open_draft_orders

User = get_user_model()


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
@permission_required('inventory.change_product', raise_exception=True)
def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/edit_product.html', {'form': form, 'product': product})


@login_required
@permission_required('inventory.delete_product', raise_exception=True)
def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('product_list')


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
    """
    Dashboard واحدة بس لكل المستخدمين. لو Owner، بيتضاف للـ context كل
    بيانات التحليلات والإدارة، والـ template نفسه بيفرز يعرض إيه بناءً على
    is_owner. لو مش Owner، بياخد نفس الصفحة بس النسخة المبسطة.
    """
    auto_created_orders = auto_generate_draft_orders()
    is_owner = request.user.is_superuser or request.user.groups.filter(name='Owner').exists()

    context = {
        'auto_created_orders': auto_created_orders,
        'is_owner': is_owner,
    }

    if is_owner:
        total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_purchases = Purchase.objects.aggregate(total=Sum('total_cost'))['total'] or 0

        context.update({
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'net_profit': total_sales - total_purchases,
            'total_products': Product.objects.count(),
            'total_suppliers': Supplier.objects.count(),
            'users': User.objects.all().prefetch_related('groups'),
            'recent_purchases': Purchase.objects.select_related('supplier').order_by('-created_at')[:10],
            'recent_sales': Sale.objects.order_by('-created_at')[:10],
        })
    else:
        context.update({
            'total_products': Product.objects.count(),
            'low_stock_products': get_low_stock_products(),
        })

    return render(request, 'inventory/dashboard.html', context)


@login_required
@permission_required('inventory.view_supplier', raise_exception=True)
def supplier_list_view(request):
    form = SupplierForm()

    if request.method == 'POST':
        if not request.user.has_perm('inventory.add_supplier'):
            raise PermissionDenied("You don't have permission to add suppliers.")
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')

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