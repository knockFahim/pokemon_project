from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pokemon/', views.pokemon_list, name='pokemon_list'),
    path('pokemon/<int:pokemon_id>/', views.pokemon_detail, name='pokemon_detail'),
    path('generate/', views.generate_pokemon, name='generate_pokemon'),
    path('my-pokemon/', views.my_pokemon, name='my_pokemon'),
    path('nickname/<int:user_pokemon_id>/', views.nickname_pokemon, name='nickname_pokemon'),
    path('release/<int:user_pokemon_id>/', views.release_pokemon, name='release_pokemon'),
    path('select-team/', views.select_pokemon, name='select_pokemon'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('logout/', views.custom_logout, name='logout'),  # Custom logout view
    path('messages/', views.message_board, name='message_board'),  # Message board view
    path('trade/create/', views.create_trade, name='create_trade'),
    path('trade/accept/<int:trade_id>/', views.accept_trade, name='accept_trade'),
    path('trade/options/<int:trade_id>/', views.get_trade_pokemon_options, name='get_trade_pokemon_options'),
]
