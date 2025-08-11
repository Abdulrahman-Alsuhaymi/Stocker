from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from products.models import Product
from .models import Contact
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.db import models

# Create your views here.

def home_view(request:HttpRequest):

    if request.user.is_authenticated:
        print(request.user.email)
    else:
        print("User is not logged in")

    
    products = Product.objects.all().order_by("-created_at")[0:3]

    return render(request, 'main/index.html', {"products" : products} )


def contact_view(request:HttpRequest):
    
    if request.method == "POST":
        contact = Contact(name=request.POST["name"], email=request.POST["email"], subject=request.POST["subject"], message=request.POST["message"])
        contact.save()

        
        content_html = render_to_string("main/mail/confirmation.html")
        send_to = contact.email
        email_message = EmailMessage("confirmation", content_html, settings.EMAIL_HOST_USER, [send_to])
        email_message.content_subtype = "html"
        email_message.send()

        messages.success(request, "Your message is received. Thank You.", "alert-success")

    return render(request, 'main/contact.html' )


def contact_messages_view(request:HttpRequest):
    
    contact_messages = Contact.objects.all().order_by("-created_at")

    return render(request, 'main/contact_messages.html', {"contact_messages" : contact_messages} )


def dashboard_view(request:HttpRequest):

    products = Product.objects.all().order_by("-created_at")
    
    low_stock_count = Product.objects.filter(
        current_stock__lte=models.F('min_stock_level')
    ).count()
    
    from datetime import date, timedelta
    today = date.today()
    threshold_date = today + timedelta(days=30)
    
    expiring_count = Product.objects.filter(
        is_perishable=True,
        expiry_date__isnull=False,
        expiry_date__lte=threshold_date
    ).count()
    
    context = {
        "products": products,
        "low_stock_count": low_stock_count,
        "expiring_count": expiring_count,
    }

    return render(request, 'main/dashboard.html', context)