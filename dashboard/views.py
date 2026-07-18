from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import FarmerProfile, Product, Cart, CartItem


# ==================== FARMER DASHBOARD ====================

@login_required
def farmer_dashboard(request):
    """Main farmer dashboard"""
    if not hasattr(request.user, 'farmer_profile'):
        FarmerProfile.objects.create(user=request.user)
    
    my_products = Product.objects.filter(farmer=request.user)
    total_products = my_products.count()
    low_stock = my_products.filter(quantity_in_stock__lt=10).count()
    
    context = {
        'my_products': my_products,
        'total_products': total_products,
        'low_stock': low_stock,
        'profile': request.user.farmer_profile,
    }
    return render(request, 'dashboard/farmer_dashboard.html', context)


@login_required
def add_product(request):
    """Farmer adds a new product with multiple sub-images"""
    if request.method == 'POST':
        # Create the main product
        product = Product(
            farmer=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            price_per_unit=request.POST.get('price_per_unit'),
            unit=request.POST.get('unit'),
            quantity_in_stock=request.POST.get('quantity_in_stock', 0),
            discount_percentage=request.POST.get('discount_percentage', 0),
            ideal_temperature=request.POST.get('ideal_temperature', ''),
            specifications=request.POST.get('specifications', ''),
            expiry_date=request.POST.get('expiry_date') or None,
        )
        
        # Save main image
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()

        # Save multiple sub-images
        sub_images = request.FILES.getlist('sub_images')
        for img in sub_images[:5]:  # Limit to 5 sub-images
            from .models import ProductImage
            ProductImage.objects.create(product=product, image=img)

        messages.success(request, f'Product "{product.name}" added successfully with {len(sub_images)} extra images!')
        return redirect('dashboard:farmer_dashboard')
   
    return render(request, 'dashboard/add_product.html')

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price_per_unit = request.POST.get('price_per_unit')
        product.unit = request.POST.get('unit')
        product.quantity_in_stock = request.POST.get('quantity_in_stock')
        product.discount_percentage = request.POST.get('discount_percentage', 0)
        product.ideal_temperature = request.POST.get('ideal_temperature', '')
        product.specifications = request.POST.get('specifications', '')
        product.expiry_date = request.POST.get('expiry_date') or None
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('dashboard:farmer_dashboard')
    
    return render(request, 'dashboard/edit_product.html', {'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('dashboard:farmer_dashboard')


@login_required
def farmer_profile(request):
    """Farmer profile management"""
    profile, created = FarmerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.farm_name = request.POST.get('farm_name')
        profile.phone = request.POST.get('phone')
        profile.location = request.POST.get('location')
        profile.description = request.POST.get('description')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard:farmer_profile')
    
    return render(request, 'dashboard/farmer_profile.html', {'profile': profile})


# ==================== INSTITUTIONAL BUYER DASHBOARD ====================

@login_required
def buyer_dashboard(request):
    """Main buyer marketplace"""
    products = Product.objects.filter(is_available=True).select_related('farmer')
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(farmer__username__icontains=search)
        )
    
    # Filter by unit
    unit = request.GET.get('unit')
    if unit:
        products = products.filter(unit=unit)
    
        # Get cart count for badge
    try:
        cart = request.user.cart
        cart_count = cart.total_items
    except:
        cart_count = 0

    context = {
        'products': products,
        'search': search or '',
        'cart_count': cart_count,
    }
    return render(request, 'dashboard/buyer_dashboard.html', context)


@login_required
def product_detail(request, pk):
    """Product detail page"""
    product = get_object_or_404(Product, pk=pk, is_available=True)
    return render(request, 'dashboard/product_detail.html', {'product': product})


@login_required
def add_to_cart(request, pk):
    """Add product to cart"""
    product = get_object_or_404(Product, pk=pk)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('dashboard:buyer_dashboard')


@login_required
def view_cart(request):
    """View shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'dashboard/cart.html', {'cart': cart})


@login_required
def update_cart_item(request, item_id):
    """Update quantity in cart"""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            item.quantity = new_quantity
            item.save()
        else:
            item.delete()
    
    return redirect('dashboard:view_cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('dashboard:view_cart')
