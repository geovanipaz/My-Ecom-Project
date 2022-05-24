from curses.ascii import HT
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib import messages

from App_Order.models import Order, Cart
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForms

from django.contrib.auth.decorators import login_required
#payment
import requests

from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@login_required
def checkout(request):
    save_address = BillingAddress.objects.get_or_create(user=request.user)
    save_address = save_address[0]
    form = BillingForms(instance=save_address)
    if request.method == 'POST':
        form = BillingForms(request.POST, instance=save_address)
        if form.is_valid():
            form.save()
            form = BillingForms(instance=save_address)
            messages.success(request,'Shipping Address saved')
            
    order_qs = Order.objects.filter(user=request.user, ordered = False)
    order_items = order_qs[0].orderitems.all()
    order_total = order_qs[0].get_totals()
    
    return render(request, 'App_Payment/checkout.html', context={
        'form':form,
        'order_items':order_items,
        'order_total':order_total,
        'saved_address':save_address})
        

@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    if not saved_address.is_fully_filled():
        messages.info(request, 'Please complete shipping address ')
        return redirect('App_Payment:checkout')
    
    if not request.user.profile.is_fully_filled():
        messages.info(request,'Please Complete profile details')
        return redirect('App_Login:profile')
    
    store_id = 'geo628bc4126a337'
    API_key = 'geo628bc4126a337@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True,
                            sslc_store_id=store_id,
                            sslc_store_pass=API_key)
    
    status_url = request.build_absolute_uri(reverse('App_Payment:complete'))
    #print(status_url)
    mypayment.set_urls(success_url=status_url,
                       fail_url=status_url, 
                       cancel_url=status_url, 
                       ipn_url=status_url)
    
    order_qs = Order.objects.filter(user=request.user, ordered= False)
    order_items = order_qs[0].orderitems.all()
    order_item_count = order_qs[0].orderitems.count()
    order_total = order_qs[0].get_totals()
    mypayment.set_product_integration(total_amount=Decimal(order_total),
                                      currency='USD',
                                      product_category='Mixed',
                                      product_name=order_items, 
                                      num_of_item=order_item_count, 
                                      shipping_method='Courier', 
                                      product_profile='None')
    current_user = request.user
    mypayment.set_customer_info(name=current_user.profile.full_name, 
                                email=current_user.email, 
                                address1=current_user.profile.address_1,
                                address2=current_user.profile.address_1, 
                                city=current_user.profile.city, 
                                postcode=current_user.profile.zip_code,
                                country=current_user.profile.country, 
                                phone=current_user.profile.phone)

    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name,
                                address=saved_address.address,
                                city=saved_address.city,
                                postcode=saved_address.zipcode,
                                country=saved_address.country)

    response_data = mypayment.init_payment()
    #print(response_data)
    return redirect(response_data['GatewayPageURL'])
    #return render(request, 'App_Payment/payment.html', context={})

@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method =='post':
        payment_data = request.POST
        status = payment_data['status']
       
        #bank_tran_id = payment_data['bank_tran_id']
        
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, 'Payment Complete Succesfully')
            return HttpResponseRedirect(reverse('App_Payment:purchase',
                                                kwargs={'val_id':val_id,
                                                        'tran_id':tran_id}))
        elif status == 'FAILED':
            messages.warning(request, 'Payment failed. Please try again.')
            
    
    return render(request, 'App_Payment/complete.html', context={})

@login_required
def purchase(request, val_id, tran_id):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    orderId = tran_id
    order.ordered = True
    order.orderId = orderId
    order.paymentId = val_id
    order.save()
    
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased = True
        item.save()
    
    return HttpResponseRedirect(reverse('App_Shop:home'))

@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {'orders':orders}
    except:
        messages.warning(request, 'You do not have an active order')
        return redirect('App_Shop:home')
    return render(request, 'App_Payment/order.html', context)