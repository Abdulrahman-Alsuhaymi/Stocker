from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from .models import Supplier
from .forms import SupplierForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.

def supplier_list_view(request:HttpRequest):
    
    suppliers = Supplier.objects.all().order_by("name")

    page_number = request.GET.get("page", 1)
    paginator = Paginator(suppliers, 6)
    suppliers_page = paginator.get_page(page_number)

    return render(request, "suppliers/supplier_list.html", {"suppliers":suppliers_page})


def supplier_create_view(request:HttpRequest):

    if not (request.user.is_staff and request.user.has_perm("suppliers.add_supplier")):
        messages.warning(request, "You don't have permission to add supplier", "alert-warning")
        return redirect("main:home_view")

    supplier_form = SupplierForm()

    if request.method == "POST":
        
        supplier_form = SupplierForm(request.POST, request.FILES)
        if supplier_form.is_valid():
            supplier = supplier_form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, "Created Supplier Successfully", "alert-success")
            return redirect('suppliers:supplier_list_view')
        else:
            print("not valid form", supplier_form.errors)

    return render(request, "suppliers/create.html", {"supplier_form":supplier_form})


def supplier_detail_view(request:HttpRequest, supplier_id:int):

    supplier = Supplier.objects.get(pk=supplier_id)

    return render(request, 'suppliers/supplier_detail.html', {"supplier" : supplier})


def supplier_update_view(request:HttpRequest, supplier_id:int):

    if not (request.user.is_staff and request.user.has_perm("suppliers.change_supplier")):
        messages.warning(request, "only staff can update supplier", "alert-warning")
        return redirect("main:home_view")
    
    supplier = Supplier.objects.get(pk=supplier_id)

    if request.method == "POST":
        supplier_form = SupplierForm(instance=supplier, data=request.POST, files=request.FILES)
        if supplier_form.is_valid():
            supplier_form.save()
        else:
            print(supplier_form.errors)

        return redirect("suppliers:supplier_detail_view", supplier_id=supplier.id)

    return render(request, "suppliers/supplier_update.html", {"supplier":supplier})


def supplier_delete_view(request:HttpRequest, supplier_id:int):

    if not (request.user.is_staff and request.user.has_perm("suppliers.delete_supplier")):
        messages.warning(request, "only staff can delete supplier", "alert-warning")
        return redirect("main:home_view")
    
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        supplier.delete()
        messages.success(request, "Deleted supplier successfully", "alert-success")
    except Exception as e:
        print(e)
        messages.error(request, "Couldn't Delete supplier", "alert-danger")

    return redirect("suppliers:supplier_list_view")


def supplier_search_view(request:HttpRequest):

    if "search" in request.GET and len(request.GET["search"]) >= 3:
        suppliers = Supplier.objects.filter(name__contains=request.GET["search"])

        if "order_by" in request.GET and request.GET["order_by"] == "name":
            suppliers = suppliers.order_by("name")
        elif "order_by" in request.GET and request.GET["order_by"] == "rating":
            suppliers = suppliers.order_by("-rating")
    else:
        suppliers = []

    return render(request, "suppliers/search_suppliers.html", {"suppliers" : suppliers})