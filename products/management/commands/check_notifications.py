from django.core.management.base import BaseCommand
from products.models import Product
from django.db import models
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Check and send low stock and expiry notifications'

    def handle(self, *args, **options):
        self.stdout.write("Checking notifications...")
        
        low_stock_products = Product.objects.filter(
            current_stock__lte=models.F('min_stock_level')
        )
        
        low_stock_count = 0
        for product in low_stock_products:
            product.send_low_stock_notification()
            low_stock_count += 1
        
        today = date.today()
        threshold_date = today + timedelta(days=30)
        
        expiring_products = Product.objects.filter(
            is_perishable=True,
            expiry_date__isnull=False,
            expiry_date__lte=threshold_date
        )
        
        expiry_count = 0
        for product in expiring_products:
            product.send_expiry_notification()
            expiry_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Notifications sent: {low_stock_count} low stock, {expiry_count} expiry alerts"
            )
        )

