from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from App_Order.models import Order, Cart
from App_Shop.models import Product

from django.contrib import messages
# Create your views here.

@login_required
def add_to_cart(request, pk):
    #pega o item
    item = get_object_or_404(Product, pk=pk)
    #coloca ou cria item no carrinho
    order_item = Cart.objects.get_or_create(
        item=item,
        user=request.user,
        purchased=False)
    #verifica se pedido já existe
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    #se existir pega o primeiro resultado e coloca em outro obj pedido
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item[0].quantity += 1
            order_item[0].save()
            messages.info(request,'This Item Quantity was Updated')   
            return redirect('App_Shop:home')          
        else:
            order.orderitems.add(order_item[0])
            messages.info(request,'This Item was Addedd in your card')
            return redirect('App_Shop:home')
    else:
        order = Order(user=request.user)
        order.save()
        order.orderitems.add(order_item[0])
        messages.info(request,'This Item was Addedd in your card')
        return redirect('App_Shop:home')