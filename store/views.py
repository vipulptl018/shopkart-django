from django.shortcuts import render, get_object_or_404
from .models import product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, Paginator,PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
# Create your views here.

# second way use get_url and context processor 



def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = product.objects.filter(category = categories, is_available = True)
        # pagination start 
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        pages_products = paginator.get_page(page)
        # pagination start end
       
        product_count = products.count
    else:
    
        products = product.objects.all().filter(is_available = True).order_by('id')
        # pagination start
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        pages_products = paginator.get_page(page)
        # pagination start end
        product_count = products.count()
    context = {
            'products':pages_products,
            'product_count': product_count
        }

    return render (request, 'store/store.html', context)


#  if are use this first way then not use category model inside get_url function simply use this store func
# def store(request, category_slug=None):
#     category = None
#     products = None

#     if category_slug != None:
#         category = get_object_or_404(Category, slug=category_slug)
#         products = product.objects.filter(category=category, is_available=True)
#         product_count = products.count()
#     else:
    
#         products = product.objects.all().filter(is_available = True)
#         product_count = products.count()
    
#     context = {
#         'products': products,
#         'category': category,
#         'product_count': product_count

#     }
#     return render (request, 'store/store.html', context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
    except  Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html',context)


#  This fun is used for search any product by desciptions and product name
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product.objects.order_by('-create_date').filter(Q(desciptions__icontains = keyword) | Q(product_name__icontains = keyword))
        product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html', context)

