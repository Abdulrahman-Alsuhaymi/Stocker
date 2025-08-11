from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard_view, name="reports_dashboard"),
    path("inventory/", views.inventory_report_view, name="inventory_report"),
    path("suppliers/", views.supplier_report_view, name="supplier_report"),
    path("low-stock/", views.low_stock_report_view, name="low_stock_report"),
    path("expiring/", views.expiring_products_report_view, name="expiring_products_report")
]