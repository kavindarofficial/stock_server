from django.urls import path
from .views import RegisterUser, LoginUser, StockList, BuyStock, SellStock

urlpatterns = [
    path('register/', RegisterUser.as_view()),
    path('login/', LoginUser.as_view()),
    path('stocks/', StockList.as_view()),
    path('buy/', BuyStock.as_view()),
    path('sell/', SellStock.as_view()),
]
