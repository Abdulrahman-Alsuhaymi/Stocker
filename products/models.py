from django.db import models
from django.contrib.auth.models import User
from suppliers.models import Supplier


# Create your models here.

class Category(models.Model):

    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    suppliers = models.ManyToManyField(Supplier)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    current_stock = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)
    
    image = models.ImageField(upload_to="products/", default="products/default.jpg")
    is_perishable = models.BooleanField(default=False)
    expiry_date = models.DateField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
    
    def is_low_stock(self):
        return self.current_stock <= self.min_stock_level
    
    def is_expiring_soon(self, days_threshold=30):
        if not self.is_perishable or not self.expiry_date:
            return False
        
        from datetime import date, timedelta
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        return self.expiry_date <= threshold_date
    
    def send_low_stock_notification(self):
        if not self.is_low_stock():
            return
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        managers = User.objects.filter(profile__is_manager=True, profile__notification_email__isnull=False).exclude(profile__notification_email='')
        
        if not managers:
            print(f"⚠️  No managers found for low stock notification: {self.name}")
            return
        
        print(f"📧 Found {managers.count()} managers for low stock notification")
        
        subject = f"Low Stock Alert: {self.name}"
        message = f"""
Low Stock Alert!

Product: {self.name}
SKU: {self.sku}
Current Stock: {self.current_stock}
Minimum Stock Level: {self.min_stock_level}
Category: {self.category.name if self.category else 'N/A'}

Please restock this item soon.
        """.strip()
        
        emails_sent = 0
        for manager in managers:
            try:
                print(f"📤 Attempting to send email to {manager.profile.notification_email}")
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[manager.profile.notification_email],
                    fail_silently=False
                )
                if result:
                    emails_sent += 1
                    print(f"✅ Email sent successfully to {manager.profile.notification_email}")
                else:
                    print(f"❌ Email failed to send to {manager.profile.notification_email}")
            except Exception as e:
                print(f"❌ Error sending email to {manager.profile.notification_email}: {e}")
        
        print(f"📧 Low stock notifications sent: {emails_sent}/{managers.count()} managers")
    
    def send_expiry_notification(self):
 
        if not self.is_expiring_soon():
            return
        
        from django.core.mail import send_mail
        from django.conf import settings
        from datetime import date
        
        managers = User.objects.filter(profile__is_manager=True, profile__notification_email__isnull=False).exclude(profile__notification_email='')
        
        if not managers:
            return
        
        subject = f"Expiry Alert: {self.name}"
        message = f"""
Expiry Alert!

Product: {self.name}
SKU: {self.sku}
Expiry Date: {self.expiry_date}
Days Until Expiry: {(self.expiry_date - date.today()).days}

This item is expiring soon. Please take action.
        """.strip()
    
        emails_sent = 0
        for manager in managers:
            try:
                print(f"📤 Attempting to send email to {manager.profile.notification_email}")
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[manager.profile.notification_email],
                    fail_silently=False
                )
                if result:
                    emails_sent += 1
                    print(f"✅ Email sent successfully to {manager.profile.notification_email}")
                else:
                    print(f"❌ Email failed to send to {manager.profile.notification_email}")
            except Exception as e:
                print(f"❌ Error sending email to {manager.profile.notification_email}: {e}")
        
        print(f"📧 Expiry notifications sent: {emails_sent}/{managers.count()} managers")
    
