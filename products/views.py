import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from .models import Product, Category
from .forms import ProductForm, CategoryForm, CSVUploadForm
from suppliers.models import Supplier
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.

def product_list_view(request:HttpRequest):
    
    products = Product.objects.all().order_by("-created_at")

    page_number = request.GET.get("page", 1)
    paginator = Paginator(products, 6)
    products_page = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {"products":products_page})


def product_create_view(request:HttpRequest):

    if not (request.user.is_staff and request.user.has_perm("products.add_product")):
        messages.warning(request, "You don't have permission to add product", "alert-warning")
        return redirect("main:home_view")

    product_form = ProductForm()
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.created_by = request.user
            product.save()
            product_form.save_m2m()
            messages.success(request, "Created Product Successfully", "alert-success")
            return redirect('main:home_view')
        else:
            print("not valid form", product_form.errors)

    return render(request, "products/create.html", {"product_form":product_form, "categories":categories, "suppliers": suppliers})


def product_detail_view(request:HttpRequest, product_id:int):

    product = Product.objects.get(pk=product_id)

    return render(request, 'products/product_detail.html', {"product" : product})


def product_update_view(request:HttpRequest, product_id:int):

    if not (request.user.is_staff and request.user.has_perm("products.change_product")):
        messages.warning(request, "only staff can update product", "alert-warning")
        return redirect("main:home_view")
    
    product = Product.objects.get(pk=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        product_form = ProductForm(instance=product, data=request.POST, files=request.FILES)
        if product_form.is_valid():
            # Get old values before saving
            old_product = Product.objects.get(pk=product_id)
            old_stock = old_product.current_stock
            old_expiry = old_product.expiry_date
            
            product_form.save()
            
            if product.current_stock < old_stock and product.is_low_stock():
                product.send_low_stock_notification()
            
            if product.is_perishable and product.expiry_date and product.is_expiring_soon():
                product.send_expiry_notification()
        else:
            print(product_form.errors)

        return redirect("products:product_detail_view", product_id=product.id)

    return render(request, "products/product_update.html", {"product":product, "categories" : categories, "suppliers": suppliers})


def product_delete_view(request:HttpRequest, product_id:int):

    if not (request.user.is_staff and request.user.has_perm("products.delete_product")):
        messages.warning(request, "only staff can delete product", "alert-warning")
        return redirect("main:home_view")
    
    try:
        product = Product.objects.get(pk=product_id)
        product.delete()
        messages.success(request, "Deleted product successfully", "alert-success")
    except Exception as e:
        print(e)
        messages.error(request, "Couldn't Delete product", "alert-danger")

    return redirect("main:home_view")



def category_create_view(request:HttpRequest):

    if not (request.user.is_staff and request.user.has_perm("products.add_category")):
        messages.warning(request, "You don't have permission to add category", "alert-warning")
        return redirect("main:home_view")

    category_form = CategoryForm()

    if request.method == "POST":
        
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Created Category Successfully", "alert-success")
            return redirect('products:category_list_view')
        else:
            print("not valid form", category_form.errors)

    return render(request, "products/category_create.html", {"category_form":category_form})


def category_update_view(request:HttpRequest, category_id:int):

    if not (request.user.is_staff and request.user.has_perm("products.change_category")):
        messages.warning(request, "only staff can update category", "alert-warning")
        return redirect("main:home_view")
    
    category = Category.objects.get(pk=category_id)

    if request.method == "POST":
        category_form = CategoryForm(instance=category, data=request.POST)
        if category_form.is_valid():
            category_form.save()
        else:
            print(category_form.errors)

        return redirect("products:category_list_view")

    return render(request, "products/category_update.html", {"category":category, "category_form": CategoryForm(instance=category)})


def category_delete_view(request:HttpRequest, category_id:int):

    if not (request.user.is_staff and request.user.has_perm("products.delete_category")):
        messages.warning(request, "only staff can delete category", "alert-warning")
        return redirect("main:home_view")
    
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        messages.success(request, "Deleted category successfully", "alert-success")
    except Exception as e:
        print(e)
        messages.error(request, "Couldn't Delete category", "alert-danger")

    return redirect("products:category_list_view")


def product_search_view(request:HttpRequest):

    if "search" in request.GET and len(request.GET["search"]) >= 3:
        products = Product.objects.filter(name__contains=request.GET["search"])

        if "order_by" in request.GET and request.GET["order_by"] == "name":
            products = products.order_by("name")
        elif "order_by" in request.GET and request.GET["order_by"] == "created_at":
            products = products.order_by("-created_at")
    else:
        products = []

    return render(request, "products/search_products.html", {"products" : products})


def category_list_view(request:HttpRequest):

    categories = Category.objects.all().order_by('name')
    
    context = {
        "categories": categories,
        "can_manage": request.user.is_staff,
    }
    
    return render(request, "products/category_list.html", context)


def check_notifications_view(request:HttpRequest):
    
    if not request.user.is_staff:
        messages.warning(request, "Only staff can check notifications", "alert-warning")
        return redirect("main:home_view")
    
    low_stock_products = Product.objects.filter(
        current_stock__lte=F('min_stock_level')
    )
    
    low_stock_count = 0
    for product in low_stock_products:
        product.send_low_stock_notification()
        low_stock_count += 1
    
    from datetime import date, timedelta
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
    
    messages.success(
        request, 
        f"Notifications sent: {low_stock_count} low stock, {expiry_count} expiry alerts", 
        "alert-success"
    )
    
    return redirect("main:home_view")


def export_products_csv(request: HttpRequest):
    
    if not request.user.is_staff:
        return redirect("main:home_view")
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Description', 'SKU', 'Category', 'Cost Price', 'Selling Price', 'Current Stock', 'Min Stock Level', 'Is Perishable', 'Expiry Date'])
    
    for product in Product.objects.all():
        writer.writerow([
            product.name, product.description, product.sku,
            product.category.name if product.category else '',
            product.cost_price, product.selling_price,
            product.current_stock, product.min_stock_level,
            'Yes' if product.is_perishable else 'No',
            product.expiry_date.strftime('%Y-%m-%d') if product.expiry_date else ''
        ])
    
    return response


def import_products_csv(request: HttpRequest):
    
    if not request.user.is_staff:
        return redirect("main:home_view")
    
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            for row in csv_data:
                try:
                    category, created = Category.objects.get_or_create(name=row['category'])
                    Product.objects.create(
                        name=row['name'],
                        description=row['description'],
                        sku=row['sku'],
                        category=category,
                        cost_price=float(row['cost_price']),
                        selling_price=float(row['selling_price']),
                        current_stock=int(row['current_stock']),
                        min_stock_level=int(row['min_stock_level']),
                        is_perishable=row['is_perishable'].lower() == 'yes',
                        expiry_date=datetime.strptime(row['expiry_date'], '%Y-%m-%d').date() if row['expiry_date'] else None,
                        created_by=request.user
                    )
                except:
                    pass
            
            messages.success(request, "Products imported", "alert-success")
            return redirect('products:product_list_view')
    else:
        form = CSVUploadForm()
    
    return render(request, 'products/import_products.html', {'form': form})


