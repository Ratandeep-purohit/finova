from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import UserProfile, Stock, Portfolio, Scenario
from .serializers import UserProfileSerializer, StockSerializer, PortfolioSerializer, ScenarioSerializer
import random
from decimal import Decimal

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    profile = UserProfile.objects.create(user=user, balance=10000.00)
    return Response({'message': 'Registered successfully', 'balance': profile.balance}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        profile = UserProfile.objects.get(user=user)
        return Response({
            'message': 'Logged in successfully',
            'profile': UserProfileSerializer(profile).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile(request):
    username = request.GET.get('username')
    profile = UserProfile.objects.get(user__username=username)
    return Response(UserProfileSerializer(profile).data)

@api_view(['GET'])
def get_leaderboard(request):
    profiles = UserProfile.objects.order_by('-xp')[:10]
    return Response(UserProfileSerializer(profiles, many=True).data)

@api_view(['GET'])
def get_stocks(request):
    # Simulate price fluctuation on fetch for demo
    for stock in Stock.objects.all():
        change_pct = random.uniform(float(-stock.volatility), float(stock.volatility))
        change_amount = float(stock.current_price) * (change_pct / 100.0)
        stock.current_price = max(Decimal('1.00'), stock.current_price + Decimal(str(round(change_amount, 2))))
        stock.save()

    stocks = Stock.objects.all()
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def buy_stock(request):
    username = request.data.get('username')
    stock_id = request.data.get('stock_id')
    quantity = int(request.data.get('quantity', 0))
    if quantity <= 0:
        return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock = Stock.objects.get(id=stock_id)
        profile = UserProfile.objects.get(user__username=username)
        total_cost = stock.current_price * quantity
        
        if profile.balance < total_cost:
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.balance -= total_cost
        profile.save()

        portfolio, created = Portfolio.objects.get_or_create(user=profile, stock=stock)
        
        # Calculate new average buy price
        old_total = portfolio.average_buy_price * portfolio.quantity
        portfolio.quantity += quantity
        portfolio.average_buy_price = (old_total + total_cost) / portfolio.quantity
        portfolio.save()

        return Response({'message': f'Successfully bought {quantity} {stock.symbol}', 'balance': profile.balance})
    except Stock.DoesNotExist:
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def sell_stock(request):
    username = request.data.get('username')
    stock_id = request.data.get('stock_id')
    quantity = int(request.data.get('quantity', 0))

    try:
        stock = Stock.objects.get(id=stock_id)
        profile = UserProfile.objects.get(user__username=username)
        portfolio = Portfolio.objects.get(user=profile, stock=stock)

        if portfolio.quantity < quantity:
            return Response({'error': 'Not enough shares'}, status=status.HTTP_400_BAD_REQUEST)

        total_earning = stock.current_price * quantity
        
        # Determine profit/loss
        cost_basis = portfolio.average_buy_price * quantity
        profit = total_earning - cost_basis

        profile.balance += total_earning
        
        # Gamification: Reward XP for profitable trades
        if profit > 0:
            profile.xp += 10
            # Level up logic
            if profile.xp >= profile.level * 100:
                profile.level += 1
                profile.xp -= profile.level * 100

        profile.save()

        portfolio.quantity -= quantity
        if portfolio.quantity == 0:
            portfolio.delete()
        else:
            portfolio.save()

        return Response({
            'message': f'Successfully sold {quantity} {stock.symbol}',
            'balance': profile.balance,
            'profit': profit,
            'xp': profile.xp
        })

    except (Stock.DoesNotExist, Portfolio.DoesNotExist):
        return Response({'error': 'Invalid stock or not owned'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_portfolio(request):
    username = request.GET.get('username')
    profile = UserProfile.objects.get(user__username=username)
    portfolios = Portfolio.objects.filter(user=profile)
    return Response(PortfolioSerializer(portfolios, many=True).data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_random_scenario(request):
    scenario_type = request.GET.get('type', 'SCAM')
    scenarios = list(Scenario.objects.filter(type=scenario_type))
    if not scenarios:
        return Response({'error': 'No scenarios found'}, status=status.HTTP_404_NOT_FOUND)
    scenario = random.choice(scenarios)
    return Response(ScenarioSerializer(scenario).data)

@api_view(['POST'])
@permission_classes([AllowAny])
def answer_scenario(request):
    username = request.data.get('username')
    scenario_id = request.data.get('scenario_id')
    action = request.data.get('action') # e.g. 'DECLINE' or 'PAY'

    try:
        scenario = Scenario.objects.get(id=scenario_id)
        profile = UserProfile.objects.get(user__username=username)

        is_correct = action.upper() == scenario.correct_action.upper()
        if is_correct:
            profile.xp += scenario.xp_reward
            msg = "Correct! You successfully navigated this scenario."
        else:
            profile.balance -= scenario.penalty
            msg = f"Oops! You lost ₹{scenario.penalty}. Lesson learned."

        # simple level up
        if profile.xp >= profile.level * 100:
            profile.level += 1
            profile.xp -= profile.level * 100

        profile.save()
        return Response({
            'correct': is_correct,
            'message': msg,
            'new_balance': profile.balance,
            'new_xp': profile.xp
        })

    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found'}, status=status.HTTP_404_NOT_FOUND)
