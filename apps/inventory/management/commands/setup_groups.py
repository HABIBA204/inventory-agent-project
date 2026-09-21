from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "بينشئ Group بتاع Owner و Employee بصلاحياتهم"

    def handle(self, *args, **options):
        owner_group, _ = Group.objects.get_or_create(name='Owner')
        all_permissions = Permission.objects.filter(content_type__app_label='inventory')
        owner_group.permissions.set(all_permissions)

        employee_group, _ = Group.objects.get_or_create(name='Employee')
        employee_permissions = Permission.objects.filter(
            content_type__app_label='inventory',
            codename__in=[
                'view_supplier',
                'view_product', 'add_product', 'change_product',
                'view_purchase', 'add_purchase',
                'view_purchaseitem', 'add_purchaseitem',
                'view_sale', 'add_sale',
                'view_saleitem', 'add_saleitem',
            ]
        )
        employee_group.permissions.set(employee_permissions)

        self.stdout.write('تم إنشاء الـ groups بنجاح')