from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Category, SparePart, Sale, Basket
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
import json

# Create your views here.

# Landing page view

def landing(request):
    return render(request, 'inventory/landing.html')

# Owner login view

def owner_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('owner_dashboard')
        else:
            return render(request, 'inventory/owner_login.html', {'error': 'Invalid credentials or not an owner.'})
    return render(request, 'inventory/owner_login.html')

# Owner dashboard (requires login)
@login_required(login_url='/owner-login/')
def owner_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    # Get sales statistics
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    monthly_sales = Sale.objects.filter(
        sale_date__month=timezone.now().month,
        sale_date__year=timezone.now().year
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Get top selling products
    top_products = Sale.objects.values('part__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Get low stock products
    low_stock_products = SparePart.objects.filter(stock__lt=10)
    
    # Get recent sales
    recent_sales = Sale.objects.select_related('part').order_by('-sale_date')[:10]
    
    # Get all products for stock management
    products = SparePart.objects.all()
    
    # Get highest and lowest selling products
    highest_selling = Sale.objects.values('part__name').annotate(
        total_sales=Sum('total_price')
    ).order_by('-total_sales')[:5]
    
    context = {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'products': products,
        'highest_selling': highest_selling,
    }
    return render(request, 'inventory/owner_dashboard.html', context)

# Customer dashboard (no login required)
def customer_dashboard(request):
    categories = Category.objects.all()
    products = SparePart.objects.all()
    
    # Get category filter from query parameters
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'inventory/customer_dashboard.html', context)

@login_required(login_url='/owner-login/')
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        category_id = request.POST['category']
        price = request.POST['price']
        stock = request.POST['stock']
        description = request.POST['description']
        
        category = Category.objects.get(id=category_id)
        SparePart.objects.create(
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description
        )
        return redirect('owner_dashboard')
    
    categories = Category.objects.all()
    return render(request, 'inventory/add_product.html', {'categories': categories})

@login_required(login_url='/owner-login/')
def edit_product(request, product_id):
    product = get_object_or_404(SparePart, id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.category_id = request.POST['category']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.description = request.POST['description']
        product.save()
        return redirect('owner_dashboard')
    
    categories = Category.objects.all()
    return render(request, 'inventory/edit_product.html', {
        'product': product,
        'categories': categories
    })

@login_required(login_url='/owner-login/')
def delete_product(request, product_id):
    product = get_object_or_404(SparePart, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('owner_dashboard')
    return render(request, 'inventory/delete_product.html', {'product': product})

@login_required(login_url='/owner-login/')
def stock_available(request):
    products = SparePart.objects.all().order_by('name')
    return render(request, 'inventory/stock_available.html', {'products': products})

@login_required(login_url='/owner-login/')
def low_stock_alert(request):
    low_stock_products = SparePart.objects.filter(stock__lt=10).order_by('stock')
    return render(request, 'inventory/low_stock_alert.html', {'products': low_stock_products})

@login_required(login_url='/owner-login/')
def sales_details(request):
    sales = Sale.objects.select_related('part').order_by('-sale_date')
    return render(request, 'inventory/sales_details.html', {'sales': sales})

@login_required(login_url='/owner-login/')
def total_sales(request):
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    monthly_sales = Sale.objects.filter(
        sale_date__month=timezone.now().month,
        sale_date__year=timezone.now().year
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    daily_sales = Sale.objects.filter(
        sale_date__date=timezone.now().date()
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    return render(request, 'inventory/total_sales.html', {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'daily_sales': daily_sales
    })

@login_required(login_url='/owner-login/')
def highest_sold_products(request):
    products = Sale.objects.values('part__name').annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    return render(request, 'inventory/highest_sold_products.html', {'products': products})

def add_to_basket(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(SparePart, id=product_id)
        if product.stock >= quantity:
            # Create or update basket item
            basket_item, created = Basket.objects.get_or_create(
                session_key=request.session.session_key,
                part=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                basket_item.quantity += quantity
                basket_item.save()
            
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not enough stock available'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            
            for item in items:
                product = get_object_or_404(SparePart, id=item['id'])
                quantity = item['quantity']
                
                if product.stock >= quantity:
                    # Create sale record
                    Sale.objects.create(
                        part=product,
                        quantity=quantity,
                        total_price=product.price * quantity
                    )
                    
                    # Update stock
                    product.stock -= quantity
                    product.save()
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Not enough stock for {product.name}'
                    })
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
