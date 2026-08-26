from django.urls import path
from . import views

urlpatterns = [

    # path('game/', views.game_list, name='test'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('avis/', views.review_list, name='review_list'),
    path('avis/<int:pk>/supprimer/', views.delete_review, name='delete_review'),
    path('', views.home, name='home'),
    path('game-list-legacy/', views.oeuvre_list, {'model_name': 'game'}, name='game_list'),
    path('<str:model_name>/', views.oeuvre_list, name='oeuvre_list'),
    path('<str:model_name>/<slug:slug>/', views.oeuvre_detail, name='oeuvre_detail'),
    path('<str:model_name>/<slug:slug>/reserve/', views.reserve_oeuvre, name='reserve_oeuvre'),
    path('<str:model_name>/<slug:slug>/avis/', views.review_oeuvre, name='review_oeuvre'),
]
