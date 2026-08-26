from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_view, name='scan_view'),
    path('scan/<str:barcode>/', views.scan_view, name='scan_view_barcode'),
    path('scan/return/<int:pk>/', views.mark_lent_returned, name='mark_lent_returned'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('avis/', views.review_list, name='review_list'),
    path('avis/<int:pk>/supprimer/', views.delete_review, name='delete_review'),
    path('', views.home, name='home'),
    path('<str:model_name>/', views.oeuvre_list, name='oeuvre_list'),
    path('<str:model_name>/<slug:slug>/', views.oeuvre_detail, name='oeuvre_detail'),
    path('<str:model_name>/<slug:slug>/reserve/', views.reserve_oeuvre, name='reserve_oeuvre'),
    path('<str:model_name>/<slug:slug>/avis/', views.review_oeuvre, name='review_oeuvre'),
]
