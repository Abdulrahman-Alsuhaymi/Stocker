from django.urls import path
from . import views


app_name = "products"

urlpatterns = [
    path("", views.product_list_view, name="product_list_view"),
    path("create/", views.product_create_view, name="product_create_view"),
    path("detail/<int:product_id>/", views.product_detail_view, name="product_detail_view"),
    path("update/<int:product_id>/", views.product_update_view, name="product_update_view"),
    path("delete/<int:product_id>/", views.product_delete_view, name="product_delete_view"),
    path("search/", views.product_search_view, name="product_search_view"),
    path("categories/", views.category_list_view, name="category_list_view"),
    path("categories/create/", views.category_create_view, name="category_create_view"),
    path("categories/update/<int:category_id>/", views.category_update_view, name="category_update_view"),
    path("categories/delete/<int:category_id>/", views.category_delete_view, name="category_delete_view"),
    path("notifications/check/", views.check_notifications_view, name="check_notifications_view"),
    path("import/", views.import_products_csv, name="import_products_csv"),
    path("export/", views.export_products_csv, name="export_products_csv")
]