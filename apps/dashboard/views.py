from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.db.models import Sum

from apps.inventory.models import Product, Supplier, Purchase, Sale

User = get_user_model()


def is_owner(user):
    return user.groups.filter(name='Owner').exists()


@login_required
def dashboard_view(request):
    if is_owner(request.user):
        return owner_dashboard(request)
    return employee_dashboard(request)


def owner_dashboard(request):
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_purchases = Purchase.objects.aggregate(total=Sum('total_cost'))['total'] or 0

    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'net_profit': total_sales - total_purchases,
        'total_products': Product.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'users': User.objects.all().prefetch_related('groups'),
        'recent_purchases': Purchase.objects.select_related('supplier').order_by('-created_at')[:10],
        'recent_sales': Sale.objects.order_by('-created_at')[:10],
    }
    return render(request, 'dashboard/owner_dashboard.html', context)


def employee_dashboard(request):
    # هنكمل الجزء ده لما تبعتلي تفاصيل الـ Employee Dashboard
    return render(request, 'dashboard/employee_dashboard.html', {})
