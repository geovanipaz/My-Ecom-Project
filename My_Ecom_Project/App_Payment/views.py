from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib import messages

from App_Order.models import Order, Cart
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForms

from django.contrib.auth.decorators import login_required
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
        'form':form,'order_items':order_items, 'order_total':order_total})
        

