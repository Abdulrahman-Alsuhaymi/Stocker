from django.urls import path
from . import views


app_name = "suppliers"

urlpatterns = [
    path("", views.supplier_list_view, name="supplier_list_view"),
    path("create/", views.supplier_create_view, name="supplier_create_view"),
    path("detail/<int:supplier_id>/", views.supplier_detail_view, name="supplier_detail_view"),
    path("update/<int:supplier_id>/", views.supplier_update_view, name="supplier_update_view"),
    path("delete/<int:supplier_id>/", views.supplier_delete_view, name="supplier_delete_view"),
    path("search/", views.supplier_search_view, name="supplier_search_view")
]