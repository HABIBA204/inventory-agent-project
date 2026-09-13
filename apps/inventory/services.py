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
