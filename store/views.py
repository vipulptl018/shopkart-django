from django.shortcuts import render, get_object_or_404
from .models import product
from category.models import Category

# Create your views here.

# second way use get_url and context processor 
def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = product.objects.filter(category = categories, is_available = True)
        product_count = products.count
    
    else:
    
        products = product.objects.all().filter(is_available = True)
        product_count = products.count()
    context = {
            'products':products,
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
    except  Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
    }
   


   
    return render(request, 'store/product_detail.html',context)