from django.urls import path

from . import views

urlpatterns = [
    path('', views.products, name='products'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
