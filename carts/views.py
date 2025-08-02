from django.shortcuts import render,redirect,get_object_or_404
from carts.models import Cart,CartItem
from store.models import product,Variation
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse,HttpResponseBadRequest

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    products = product.objects.get(id = product_id)  # get product
        # cart variation code start
    product_variation = []
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            # print(f"Key: {key}, Value: {value}")  #  Debug each key-value pair

            try:
                variation= Variation.objects.get(products = products,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
                # print("Matched Variation:", product_variation)
            except :
                pass
                # print(f" No match for category={key}, value={value}")

        # cart variation code end
            # print(key,value)

        # color = request.POST['color']
        # size = request.POST['size']

        # if not color:
        #     return HttpResponseBadRequest("Color not selected.")

        # return HttpResponse(f"Selected color: {color},{size}")

    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) # get the cart using the cart_id present in session
    except Cart.DoesNotExist:
        cart = Cart.objects.create( cart_id = _cart_id(request) )
    cart.save()

    is_cart_items_exits = CartItem.objects.filter(product = products, cart = cart).exists()
    if is_cart_items_exits:
        cart_item = CartItem.objects.filter(product = products, cart = cart)
        print("exist variation")
        # existing_variation = database
        # current_variation = product_variation
        # item_id = database
        ex_var_list=[]
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        if product_variation in ex_var_list:
            print("exist variation in list ")
            # icrease the cart item quantity 
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=products, id = item_id)
            item.quantity += 1
            item.save()
        else:
            print("exist variation not in  list then create varition ")
            item = CartItem.objects.create(product=products, quantity = 1,  cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        print("is_cart_items_exits variation not exist then create varition ")

        cart_item = CartItem.objects.create(
            product = products,
            quantity = 1,
            cart = cart,
        )
        if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart')


# remove inside cart qyantity this func using minus qyantity form cart 
def cart_quantity_remove(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    products = get_object_or_404(product, id = product_id)
    try:
        cart_item = CartItem.objects.get(cart = cart, product = products, id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()    
        else:
            cart_item.delete()
    except : 
        pass
    return redirect('cart')

#  this fun using remove item from cart 
def remove_cart_items(request, product_id, cart_item_id):
        cart = Cart.objects.get(cart_id = _cart_id(request))
        products = get_object_or_404(product, id = product_id)
        cart_item = CartItem.objects.get(cart = cart, product = products, id = cart_item_id)
        cart_item.delete()
        return redirect('cart')

 
 # thiss fun used for inside card qyantity total value of product total itmes in cards total frand total 
def cart(request, total = 0, quantity = 0, cart_items = None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += (cart_item.quantity)
        tax = (2*total/100)
        grand_total = total + tax
    except ObjectDoesNotExist :
        pass #just ignore
    
    context = {

        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html',context)