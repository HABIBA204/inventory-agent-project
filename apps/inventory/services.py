from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F

from .models import Product, Purchase, PurchaseItem


def get_low_stock_products():
    return (
        Product.objects.filter(stock_quantity__lte=F("min_stock_level"))
        .select_related("supplier")
        .order_by("supplier__name", "name")
    )


def suggest_reorder_quantity(product):
    # simple rule for now: bring stock back up to double the minimum level
    target = product.min_stock_level * 2
    return max(target - product.stock_quantity, product.min_stock_level)


def create_draft_purchase_orders(user, product_ids=None):
    if not user.has_perm("inventory.can_create_draft_po"):
        raise PermissionDenied("You don't have permission to create purchase orders.")

    products = get_low_stock_products()
    if product_ids:
        products = products.filter(id__in=product_ids)

    products = list(products)
    if not products:
        return []

    # group by supplier since each PO should go to a single supplier
    by_supplier = {}
    for product in products:
        by_supplier.setdefault(product.supplier_id, []).append(product)

    created = []
    with transaction.atomic():
        for supplier_id, items in by_supplier.items():
            purchase = Purchase.objects.create(
                supplier_id=supplier_id,
                status=Purchase.STATUS_DRAFT,
                created_by=user,
                total_cost=Decimal("0"),
            )
            total = Decimal("0")
            for product in items:
                qty = suggest_reorder_quantity(product)
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=qty,
                    unit_cost=product.cost_price,
                )
                total += product.cost_price * qty
            purchase.total_cost = total
            purchase.save(update_fields=["total_cost"])
            created.append(purchase)

    return created


# ============================================================
#  كشف تلقائي للنواقص + تجهيز مسودة طلب شراء تلقائياً
# ============================================================

OPEN_PURCHASE_STATUSES = [Purchase.STATUS_DRAFT, Purchase.STATUS_PENDING, Purchase.STATUS_ORDERED]


def get_products_needing_reorder():
    """
    المنتجات الناقصة اللي:
    1) ليها مورد مسجل (عشان نقدر نطلب منه أصلاً)
    2) معندهاش طلب شراء مفتوح حالياً (عشان منكررش نفس الطلب كل شوية)
    """
    low_stock_products = get_low_stock_products()

    product_ids_with_open_orders = set(
        PurchaseItem.objects.filter(purchase__status__in=OPEN_PURCHASE_STATUSES)
        .values_list("product_id", flat=True)
    )

    return [
        p for p in low_stock_products
        if p.supplier_id is not None and p.id not in product_ids_with_open_orders
    ]


def auto_generate_draft_orders():
    """
    بتتنفذ تلقائياً (من صفحة الداشبورد أو قائمة المنتجات) - بتدور على أي منتج
    قلّ عن الحد الأدنى ومعندوش طلب شراء مفتوح، وتجهزله مسودة طلب شراء من نفس
    المورد المسجل عليه، من غير أي تدخل من اليوزر.
    """
    products = get_products_needing_reorder()
    if not products:
        return []

    by_supplier = {}
    for product in products:
        by_supplier.setdefault(product.supplier_id, []).append(product)

    created = []
    with transaction.atomic():
        for supplier_id, items in by_supplier.items():
            purchase = Purchase.objects.create(
                supplier_id=supplier_id,
                status=Purchase.STATUS_DRAFT,
                created_by=None,  # اتعمل تلقائياً من النظام مش من يوزر معين
                total_cost=Decimal("0"),
            )
            total = Decimal("0")
            for product in items:
                qty = suggest_reorder_quantity(product)
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=qty,
                    unit_cost=product.cost_price,
                )
                total += product.cost_price * qty
            purchase.total_cost = total
            purchase.save(update_fields=["total_cost"])
            created.append(purchase)

    return created


def get_open_draft_orders():
    """كل طلبات الشراء اللي لسه في حالة draft (يدوية أو تلقائية) - للعرض في التقارير والشات."""
    return (
        Purchase.objects.filter(status=Purchase.STATUS_DRAFT)
        .select_related("supplier")
        .prefetch_related("item__product")
        .order_by("-created_at")
    )


# ============================================================
#  الجزء الجديد: تقليل كمية منتج معين (تسجيل بيع/تعديل يدوي)
#  الشات بوت هيقدر ينفذها لو اليوزر طلب منه بوضوح
# ============================================================

def decrease_product_stock(user, product_name, quantity):
    """
    بتقلل كمية منتج معين بمقدار quantity (مينفعش الكمية تنزل تحت صفر).
    البحث عن المنتج بيتم بالاسم (بحث تقريبي)، وده كافي لمشروع بسيط.
    """
    if not user.has_perm("inventory.change_product"):
        raise PermissionDenied("You don't have permission to update product stock.")

    if not quantity or quantity <= 0:
        raise ValueError("الكمية المطلوب تقليلها لازم تكون رقم أكبر من صفر.")

    product = Product.objects.filter(name__icontains=product_name).first()
    if not product:
        return None

    product.stock_quantity = max(product.stock_quantity - quantity, 0)
    product.save(update_fields=["stock_quantity"])
    return product