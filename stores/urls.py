from django.urls import path

from . import views


urlpatterns = [
    path('',views.index,name='index'),
    path('singlepage/<slug:slug>/',views.singlepage,name='singlepage'),

    path('search/',views.search,name='search'),

    path('addtocart/<int:id>/',views.addtocart,name='addtocart'),
    path('myCart/',views.myCart,name='myCart'),
    path('manageCart/<int:id>/',views.manageCart,name='manageCart'),
    path('emptyCart/',views.emptyCart,name='emptyCart'),
    path('checkout/',views.checkout,name='checkout'),
    # user
    path('register/',views.register,name='register'),
    path('login/',views.userlogin,name='login'),
    path('logoutuser/',views.logoutuser,name='logoutuser'),

    path('profile',views.profile,name='profile'),

    # payment methods
    path('transfer/',views.transferPage,name='transfer'),
    path('payment/<int:id>/',views.paymentPage,name='payment'),
    path('<str:ref>/',views.verify_payment,name='verify-payment'),
    


    
]
