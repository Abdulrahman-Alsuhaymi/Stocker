from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from products.models import Product, Category
from suppliers.models import Supplier
from django.contrib import messages
from django.db.models import F

# Create your views here.

def reports_dashboard_view(request:HttpRequest):

    if not request.user.is_staff:
        messages.warning(request, "Access denied. Staff privileges required.", "alert-warning")
        return redirect("main:home_view")

    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_categories = Category.objects.count()

    return render(request, 'reports/dashboard.html', {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_categories": total_categories,
    })


def inventory_report_view(request:HttpRequest):

    if not request.user.is_staff:
        messages.warning(request, "Access denied. Staff privileges required.", "alert-warning")
        return redirect("main:home_view")

    products = Product.objects.all().order_by("name")

    return render(request, 'reports/inventory_report.html', {"products": products})


def supplier_report_view(request:HttpRequest):

    if not request.user.is_staff:
        messages.warning(request, "Access denied. Staff privileges required.", "alert-warning")
        return redirect("main:home_view")

    suppliers = Supplier.objects.all().order_by("name")

    return render(request, 'reports/supplier_report.html', {"suppliers": suppliers})


def low_stock_report_view(request:HttpRequest):

    if not request.user.is_staff:
        messages.warning(request, "Access denied. Staff privileges required.", "alert-warning")
        return redirect("main:home_view")

    low_stock_products = Product.objects.filter(current_stock__lte=F('min_stock_level')).order_by("current_stock")

    return render(request, 'reports/low_stock_report.html', {"products": low_stock_products})


def expiring_products_report_view(request:HttpRequest):

    if not request.user.is_staff:
        messages.warning(request, "Access denied. Staff privileges required.", "alert-warning")
        return redirect("main:home_view")

    from datetime import date, timedelta
    expiring_products = Product.objects.filter(
        is_perishable=True,
        expiry_date__lte=date.today() + timedelta(days=30)
    ).order_by("expiry_date")

    return render(request, 'reports/expiring_products_report.html', {"products": expiring_products})
