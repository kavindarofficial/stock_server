from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from trading.models import Profile, StockHolding
import finnhub

# Initialize Finnhub client (Use your API key)
finnhub_client = finnhub.Client(api_key="cv48q2pr01qn2ga8psrgcv48q2pr01qn2ga8pss0")

# ✅ User Registration (Manually Adding Users, So Not Needed)
# ✅ Login - JWT Already Handled by TokenObtainPairView

# 🔹 Buy Stock
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_stock(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    stock_symbol = request.data.get("symbol")
    quantity = int(request.data.get("quantity", 0))

    # Fetch stock price
    stock_data = finnhub_client.quote(stock_symbol)
    current_price = stock_data["c"]

    total_cost = current_price * quantity

    # Check if user has enough balance
    if profile.balance < total_cost:
        return Response({"error": "Insufficient funds"}, status=400)

    # Deduct balance and add stock holding
    profile.balance -= total_cost
    profile.save()

    holding, created = StockHolding.objects.get_or_create(user=user, stock_symbol=stock_symbol)
    holding.quantity += quantity
    holding.save()

    return Response({
        "message": "Stock purchased successfully",
        "remaining_balance": profile.balance,
        "stock_holdings": list(StockHolding.objects.filter(user=user).values('stock_symbol', 'quantity'))
    })

# 🔹 Sell Stock
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_stock(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    stock_symbol = request.data.get("symbol")
    quantity = int(request.data.get("quantity", 0))

    stock_data = finnhub_client.quote(stock_symbol)
    current_price = stock_data["c"]

    holding = StockHolding.objects.filter(user=user, stock_symbol=stock_symbol).first()

    if not holding or holding.quantity < quantity:
        return Response({"error": "Not enough stocks to sell"}, status=400)

    # Process sale
    total_earnings = current_price * quantity
    profile.balance += total_earnings
    profile.save()

    holding.quantity -= quantity
    if holding.quantity == 0:
        holding.delete()
    else:
        holding.save()

    return Response({
        "message": "Stock sold successfully",
        "remaining_balance": profile.balance,
        "stock_holdings": list(StockHolding.objects.filter(user=user).values('stock_symbol', 'quantity'))
    })

# 🔹 Get User's Stock Holdings
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_holdings(request):
    user = request.user
    holdings = StockHolding.objects.filter(user=user).values('stock_symbol', 'quantity')

    return Response({
        "username": user.username,
        "stock_holdings": list(holdings)
    })
