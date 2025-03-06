from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .models import Stock, Portfolio, Transaction
from .serializers import StockSerializer, PortfolioSerializer, TransactionSerializer

# API Key for new stock market API
API_KEY = "your_new_stock_api_key"
STOCK_API_URL = "https://s3.tradingview.com/tv.js"  # Replace with actual API

class RegisterUser(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        Portfolio.objects.create(user=user)  # Create portfolio for new user
        return Response({"message": "User created successfully"})

class LoginUser(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=400)

class StockList(APIView):
    def get(self, request):
        response = requests.get(f"{STOCK_API_URL}?apikey={API_KEY}")
        if response.status_code == 200:
            data = response.json()
            return Response(data)
        return Response({"error": "Unable to fetch stock data"}, status=500)

class BuyStock(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        symbol = request.data.get("symbol")
        quantity = int(request.data.get("quantity"))

        # Fetch stock price from API
        response = requests.get(f"{STOCK_API_URL}/{symbol}?apikey={API_KEY}")
        if response.status_code != 200:
            return Response({"error": "Stock not found"}, status=404)
        
        stock_data = response.json()
        stock, _ = Stock.objects.get_or_create(symbol=symbol, defaults={"name": stock_data['name'], "current_price": stock_data['price']})

        total_price = stock_data['price'] * quantity
        portfolio = Portfolio.objects.get(user=user)

        if portfolio.balance < total_price:
            return Response({"error": "Insufficient funds"}, status=400)

        # Deduct balance and save transaction
        portfolio.balance -= total_price
        portfolio.save()

        Transaction.objects.create(user=user, stock=stock, quantity=quantity, price_at_transaction=stock_data['price'], transaction_type="BUY")

        return Response({"message": "Stock purchased successfully"})

class SellStock(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        symbol = request.data.get("symbol")
        quantity = int(request.data.get("quantity"))

        # Fetch stock price
        response = requests.get(f"{STOCK_API_URL}/{symbol}?apikey={API_KEY}")
        if response.status_code != 200:
            return Response({"error": "Stock not found"}, status=404)
        
        stock_data = response.json()
        stock = Stock.objects.filter(symbol=symbol).first()
        if not stock:
            return Response({"error": "Stock not owned"}, status=400)

        # Get transactions for this stock
        transactions = Transaction.objects.filter(user=user, stock=stock, transaction_type="BUY")
        owned_quantity = sum(t.quantity for t in transactions)

        if owned_quantity < quantity:
            return Response({"error": "Not enough stock to sell"}, status=400)

        # Add balance
        portfolio = Portfolio.objects.get(user=user)
        portfolio.balance += stock_data['price'] * quantity
        portfolio.save()

        Transaction.objects.create(user=user, stock=stock, quantity=quantity, price_at_transaction=stock_data['price'], transaction_type="SELL")

        return Response({"message": "Stock sold successfully"})
