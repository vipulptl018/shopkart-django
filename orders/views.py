from django.shortcuts import render, redirect
from django.http import JsonResponse

from carts.models import CartItem, Cart
from .forms import OrderForm
from .models import Order,OrderProduct,Payment
from store.models import product
import datetime
import json
# Create your views here.

#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def Place_order(request):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop 
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax     = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax     = (2*total)/100
    grand_total = total + tax

    if request.method == "POST":
        form   = OrderForm(request.POST)
        if form.is_valid():
            # store all belling inforamation on inside order table
            data = Order()
            data.user = current_user

            data.first_name = form.cleaned_data['first_name']
            data.last_name  = form.cleaned_data['last_name']
            data.phone      = form.cleaned_data['phone']
            data.email      = form.cleaned_data['email']
            data.address_line1  = form.cleaned_data['address_line1']
            data.address_line2  = form.cleaned_data['address_line2']
            data.country    = form.cleaned_data['country']
            data.city       = form.cleaned_data['city']
            data.state      = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.tax        = tax
            data.order_total = grand_total
            data.ip   = request.META.get('REMOTE_ADDR')
            data.save()
            
            # Genrate Order Number
            # today = datetime.date.today()
            # yr = today.year
            # mt = today.month
            # dt = today.day
            # current_date = f"{yr}{dt:02}{mt:02}" #O/P 20251308

            # same thing but deffrent way
            yr  = int(datetime.date.today().strftime('%Y'))
            dt  = int(datetime.date.today().strftime('%d'))
            mt  = int(datetime.date.today().strftime('%m'))
            d   = datetime.date(yr, mt, dt)
            current_date = datetime.date.today().strftime('%Y%d%m')  # YYYYDDMM #O/P 20251308
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            print("This POST method")

            order = Order.objects.get(user = current_user,is_ordered= False, order_number = order_number )
            context ={
                 'order': order,
                 'cart_items' : cart_items,
                 'grand_total' : grand_total,
                 'tax' : tax,
                 'total':total,
            }     
                 
            return render(request, 'orders/payment.html', context)
    else:
            print("This GET method")
    return redirect('checkout')
    



def payment(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'])
    #  Store trans details inside payment model 
    payment = Payment(
         user = request.user,
         payment_id = body['transID'],
         payment_method = body['payment_method'],
         amount_paid = order.order_total,
         status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()


    # Move the cart items to order product table
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id   = request.user.id
        orderproduct.product_id   = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered  = True
        orderproduct.save()

        # variation added after payment done 
        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


    # Reduce the quantity of sold product

        products = product.objects.get(id = item.product_id)
        products.stock -= item.quantity
        products.save()


    # clear cart

    cart_item = CartItem.objects.filter(user = request.user).delete()


    # Send order recived email to customer 

    mail_subject = 'Thank you for your order !'
    message = render_to_string('orders/order_recived_email.html', {
        'user': request.user,
        'order':order,
    })

    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

        # Example
    # vipul.ptl.018@gmail.com
    # 4:12 PM (12 minutes ago)
    # to vipul.ptl.18

    # Hi admin,

    # Your Orders has been recieved
    # Order Number : 2025200836
    # ---------/-----------

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
         'order_number': order.order_number,
         'transID': payment.payment_id,
    }

    return JsonResponse(data)

# complete order to billing 

def order_complete(request):
     
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")
    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)

        payment = Payment.objects.get(payment_id=transID)

        subtotal = 0
        for i in ordered_product:
            subtotal += i.product_price * i.quantity

        context ={
            'order':order,
            'order_products':ordered_product,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment':payment,
            'sub_total':subtotal,

        }
        return render(request, 'orders/order_complete.html',context)
    
    except (Payment.DoesNotExist, Order.DoesNotExist):

        return redirect('home')

     
    return render(request, 'orders/order_complete.html')