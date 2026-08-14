from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('privacy/', views.legal_document, {'slug': 'privacy'}, name='privacy'),
    path('offer/', views.legal_document, {'slug': 'offer'}, name='offer'),
]
