from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from trading.views import buy_stock, sell_stock, stock_holdings

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Get access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('buy/', buy_stock, name='buy_stock'),
    path('sell/', sell_stock, name='sell_stock'),
    path('holdings/', stock_holdings, name='stock_holdings'),  # New API to check holdings
]
