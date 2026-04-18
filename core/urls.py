from django.urls import path
from . import views

urlpatterns = [
    path('lang/',                                   views.lang_switch,          name='lang_switch'),
    path('',                                        views.home,                 name='home'),
    path('donations/',                              views.donations,            name='donations'),
    path('donations/<int:pk>/pay/',                 views.donations_pay,        name='donations_pay'),
    path('donations/<int:pk>/verify/',              views.donations_verify,     name='donations_verify'),
    path('seva/',                                   views.seva,                 name='seva'),
    path('seva/<int:pk>/pay/',                      views.seva_booking_pay,     name='seva_booking_pay'),
    path('seva/<int:pk>/verify/',                   views.seva_booking_verify,  name='seva_booking_verify'),
    path('payment-success/',                        views.payment_success,      name='payment_success'),
    path('events/',                                 views.events,               name='events'),
    path('about/',                                  views.about,                name='about'),
    path('contact/',                                views.contact,              name='contact'),
]
