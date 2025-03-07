from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer
from .utils import get_stock_price

@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "User registered successfully"}, status=201)
            return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = authenticate(username=data.get("username"), password=data.get("password"))
            if user:
                return JsonResponse({"message": "Login successful"})
            return JsonResponse({"error": "Invalid credentials"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def buy_stock(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username, symbol, quantity = data.get("username"), data.get("symbol"), int(data.get("quantity", 1))
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)

            stock_price = get_stock_price(symbol)
            if stock_price is None:
                return JsonResponse({"error": "Invalid stock symbol"}, status=400)

            total_cost = stock_price * quantity + 0  # Add $5 as transaction fee
            if profile.balance < total_cost:
                return JsonResponse({"error": "Insufficient balance"}, status=400)

            profile.balance -= total_cost
            profile.stocks[symbol] = profile.stocks.get(symbol, 0) + quantity
            profile.save()

            return JsonResponse({"message": "Stock bought successfully", "balance": profile.balance})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def sell_stock(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username, symbol, quantity = data.get("username"), data.get("symbol"), int(data.get("quantity", 1))
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)

            if profile.stocks.get(symbol, 0) < quantity:
                return JsonResponse({"error": "Not enough stocks to sell"}, status=400)

            stock_price = get_stock_price(symbol)
            if stock_price is None:
                return JsonResponse({"error": "Invalid stock symbol"}, status=400)

            profile.balance += stock_price * quantity - 5  # Deduct $5 transaction fee
            profile.stocks[symbol] -= quantity
            if profile.stocks[symbol] == 0:
                del profile.stocks[symbol]
            profile.save()

            return JsonResponse({"message": "Stock sold successfully", "balance": profile.balance})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)
