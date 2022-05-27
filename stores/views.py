from django.shortcuts import render,redirect

# paystack
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


from django.contrib.auth.decorators import login_required
from django.conf import settings


from django.core.paginator import Paginator

from django.db.models import Q
from django.contrib import messages

from . models import *
from .forms import CustomerRegister, CheckoutForm
from django.contrib.auth.models import User

from django.contrib.auth import login,logout,authenticate
# Create your views here.

def index(request):
    # getting all cart product
    getProduct = CartProduct.objects.all()
    totalproduct = getProduct.count()
    # for slider
    sliders = Curousel.objects.all()
    # products
    product = Product.objects.all().order_by('-created_at')
    # paginator
    paginator = Paginator(product,4)
    page_number = request.GET.get('page')
    product_list = paginator.get_page(page_number)
    context ={
        'sliders':sliders,
        'product':product,
        'paginator':product_list,
        'count':totalproduct
    }
    return render(request,'stores/index.html',context)

def singlepage(request,slug):
    product = Product.objects.get(slug=slug)
    product.view_count +=1
    product.save()
    context={
        'product':product
    }
    return render(request,'stores/singleproduct.html',context)



# add product to cart
def addtocart(request,id):
    # get the
    cart_product = Product.objects.get(id=id)
    # check if cart exists
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart_item = Cart.objects.get(id=cart_id)
        this_product_in_cart = cart_item.cartproduct_set.filter(product=cart_product)
        # # assign cart to user
        if request.user.is_authenticated and request.user.customer:
                cart_item.customer = request.user.customer
                cart_item.save()
        # # end
        # checking if item exist in cart
        if this_product_in_cart.exists():
            cartproduct = this_product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.subtotal += cart_product.price
            cartproduct.save()
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request, 'Item increase in cart')
        # new item in cart
        else:
            cartproduct = CartProduct.objects.create(
                cart=cart_item, product=cart_product, rate=cart_product.price, quantity=1, subtotal=cart_product.price)
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request, 'New item added to cart')

    else:
        cart_item = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_item.id
        cartproduct = CartProduct.objects.create(cart=cart_item, product =cart_product, rate = cart_product.price, quantity=1, subtotal=cart_product.price)
        cart_item.total += cart_product.price
        cart_item.save()
        messages.success(request, 'New Item to cart')
    return redirect('index')


def myCart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
        # end
    else:
        cart = None
    context = {
        'cart':cart,
    }
    return render(request, 'stores/mycart.html',context)


# manage cart
def manageCart(request,id):
    action = request.GET.get('action')
    cart_obj = CartProduct.objects.get(id=id)
    cart = cart_obj.cart

    if action == 'inc':
        cart_obj.quantity += 1
        cart_obj.subtotal += cart_obj.rate
        cart_obj.save()
        cart.total += cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity increase in cart')

    elif action == 'dcr':
        cart_obj.quantity -= 1
        cart_obj.subtotal -= cart_obj.rate
        cart_obj.save()
        cart.total -= cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity decrease in cart')

        if cart_obj.quantity == 0:
            cart_obj.delete()
    elif action == 'rmv':
        cart.total -= cart_obj.subtotal
        cart.save()
        cart_obj.delete()
        messages.success(request, 'Item remove in cart')

    else:
        pass
    return redirect('myCart')

# empty cart

def emptyCart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
        # end
        cart.cartproduct_set.all().delete()
        cart.total = 0
        cart.save()
        messages.success(request, 'All Item in cart deleted')

    return redirect('myCart')




#  checkout
def checkout(request):
    cart_id = request.session.get('cart_id', None)
    cart_obj = Cart.objects.get(id=cart_id)
    form = CheckoutForm()

    # checkout authentication
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('/login/?next=/checkout/')
    # getting cart
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        # assign to cart
        if request.user.is_authenticated and request.user.customer:
            cart_obj.customer = request.user.customer
            cart_obj.save()
        # end
    else:
        cart_obj = None
    
    # form
    if request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.cart = cart_obj
            form.discount = 0
            form.subtotal = cart_obj.total
            form.amount = cart_obj.total
            form.order_status = 'Order Received'
            pay_mth = form.payment_method
            del request.session['cart_id']
            pay_mth = form.payment_method
            form.save()
            order = form.id
            if pay_mth == 'Paystack':
                return redirect('payment', id =order)
            elif pay_mth == 'Payment Transfer':
                return redirect('transfer')

            messages.success(request, 'Order have been placed successfully')
            return redirect('index')
        else:
            messages.error(request, 'No Order have been placed')
            return redirect('index')

    context = {
        'cart':cart_obj,
        'form':form,
    }
    return render(request, 'stores/checkout.html',context)


#########Payment #####

# transfer payment
def transferPage(request):
    return render(request, 'stores/transfer.html')


# paystack payment
def paymentPage(request,id):
   
    orders = Order.objects.get(id=id)

    context = {
        'order':orders,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY 
    }
    return render(request, 'stores/payment.html',context)


# verify payment
def verify_payment(request: HttpRequest, ref:str ) -> HttpResponse:
    payment = get_object_or_404(Order, ref = ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, 'Verification Successfully')
    else:
        messages.error(request, 'Verification Failed')
    return redirect('profile')



# customer register

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = CustomerRegister()
    if request.method == 'POST':
        form = CustomerRegister(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if User.objects.filter(username= username).exists():
                messages.warning(request,'User already exist')
                return redirect('register')
            if User.objects.filter(email=email).exists():
                messages.warning(request,'Email already exist')
                return redirect('register')
            if password != password2:
                messages.warning(request,'Password not match')
                return redirect('register')
            user = User.objects.create_user(username,email,password)
            form = form.save(commit=False)
            form.user = user
            form.save()
            messages.success(request, 'User registered successfully !')
            if "next" in request.GET:
                next_url=request.GET.get("next")
                return redirect(next_url)
            else:
                return redirect('login')
    context = {
        'form':form
    }
    return render(request, 'stores/register.html',context)

# customer login
def userlogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        users = authenticate(request, username =username,password=password)
        if users is not None:
            login(request,users)
            messages.success(request,'User login successfully!')
            if "next" in request.GET:
                next_url=request.GET.get("next")
                return redirect(next_url)
            
        else:
            messages.error(request,'Username/Password not correct!')

    return render(request, 'stores/login.html')


def logoutuser(request):
    logout(request)
    messages.success(request,'User logged out successfully !')
    return redirect ('login')



@login_required(login_url='/login/')
def profile(request):
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('/loginuser/?next=/profile/')

    customer = request.user.customer
    orders = Order.objects.filter(cart__customer = customer).order_by('-id')
    context = {
        'customer':customer,
        'orders':orders,
    }
    
    return render(request, 'stores/userprofile.html',context)





# Search engine
def search(request):
    kword = request.GET.get('keyword')
    result = Product.objects.filter(Q(description__icontains=kword) | Q(title__icontains=kword) )
    context={
        'product':result
    }
    return render(request,'stores/search.html',context)
    