import stripe
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from urllib import request
from django.views import View
from flask import jsonify
from flask import Flask, render_template, jsonify, request
from .models import Product, Customer, Cart, Payment, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.conf import settings
import json
from django.views.generic import TemplateView

from .server import calculate_order_amount, app

stripe.api_key = settings.STRIPE_KEY_SECRET


# Create your views here.

def home(request):
    return render(request, 'app/home.html')


def about(request):
    return render(request, 'app/about.html')


def contact(request):
    return render(request, 'app/contact.html')


class CategoryView(View):
    def get(self, request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "app/category.html", locals())


class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html", locals())


class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, "app/productdetail.html", locals())


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Register Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/customerregistration.html', locals())


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            area = form.cleaned_data['area']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, area=area,
                           zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulation! Profile save successfully")
        else:
            messages.warning(request, "Invalid Input Data")

        return render(request, 'app/profile.html', locals())


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', locals())


class UpdateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/UpdateAddress.html', locals())

    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.area = form.cleaned_data['area']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulation! Profile Update successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    if Cart.objects.filter(product=product_id).exists():
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        return redirect('/cart')
    else:
        pass
        product = Product.objects.get(id=product_id)
        Cart(user=user, product=product).save()
        return redirect('/cart')


def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    return render(request, 'app/addtocart.html', locals())


class orders(View):
    def calculate_order_amount(items):
        # Replace this constant with a calculation of the order's amount
        # Calculate the order total on the server to prevent
        # people from directly manipulating the amount on the client
        return 1400

    def create_payment(request):
        try:
            data = json.loads(request.data)
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=calculate_order_amount(data['items']),
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return jsonify({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return jsonify(error=str(e)), 403


class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        # for p in cart_items:
        #     value = p.quantity * p.product.discounted_price
        #     famount = famount + value
        #     for p in cart_items:
        #         value = p.quantity * p.product.discounted_price
        #         famount = famount + value
        # totalamount = famount + 40
        # stripeamount = int(totalamount * 100)
        # client = auth = (settings.STRIPE_KEY_ID, settings.STRIPE_KEY_SECRET)
        # data = {"amount": stripeamount, "currency": "Dolas", "receipt": "order_rcptid_12"}
        # payment_response = orders.create_payment
        # order_id = payment_response['id']
        # order_status = payment_response['status']
        # if order_status == 'created':
        #     payment = Payment(
        #         user=user,
        #         amount=totalamount,
        #         stripe_order_id=order_id,
        #         stripe_payment_status=order_status
        #     )
        #     payment.save()
        return render(request, 'app/checkout.html', locals())


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000/"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_times=[
                {
                    'prices_data': {
                        'currency': 'Dolas',
                        'totalamount': 'totalamount',
                        'product_data': {
                            'name': 'Product'
                        },
                    },
                    'quantity': 1,
                }
            ],
            model='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"
    product = Product.objects.get(name="Product")
    def get_context_data(self, **kwargs):
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


def payment_done(request):
    pass
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    #     print("payment_done : old = ", order_id, "pid = ", payment_id, " cid= ",cust_id)
    user = request.user
    #     return redirect ("orders")
    customer = Customer.objects.get(id=cust_id)
    #     To update payment status and payment id
    payment = Payment.objects.get(stripe_order_id=order_id)
    payment.paid = True
    payment.stripe_payment_id = payment_id
    payment.save()
    #     To save order details
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, porduct=c.product, quantity=c.quantity, payment=payment).save()
        c.delete()
    return redirect("orders")


def plus_cart(request):
    product_id = request.GET.get('prod_id')
    if Cart.objects.filter(product=product_id).exists():
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        # print(prod_id)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


def minus_cart(request):
    product_id = request.GET.get('prod_id')
    if Cart.objects.filter(product=product_id).exists():
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        # print(prod_id)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


def remove_cart(request):
    product_id = request.GET.get('prod_id')
    if Cart.objects.filter(product=product_id).exists():
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        # print(prod_id)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
