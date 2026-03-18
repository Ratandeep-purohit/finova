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
    email = request.data.get('email', '').strip()
    phone_number = request.data.get('phone_number', '').strip()

    # MySQL treats "" as a unique value. We must use None if empty
    if not phone_number:
        phone_number = None
    if not email:
        email = None
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not email and not phone_number:
        return Response({'error': 'Email or Phone Number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
    if email and User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
    if phone_number and UserProfile.objects.filter(phone_number=phone_number).exists():
        return Response({'error': 'Phone number is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    profile = UserProfile.objects.create(user=user, phone_number=phone_number, balance=10000.00)
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

@api_view(['POST'])
@permission_classes([AllowAny])
def claim_mission_reward(request):
    username = request.data.get('username')
    xp = request.data.get('xp', 0)
    try:
        profile = UserProfile.objects.get(user__username=username)
        profile.xp += int(xp)
        if profile.xp < 0:
            profile.xp = 0
            
        # Optional basic leveling up formula: level = (xp / 500) + 1
        new_level = (profile.xp // 500) + 1
        if new_level > profile.level:
            profile.level = new_level
            
        profile.save()
        return Response({'message': 'Reward claimed!', 'xp': profile.xp, 'level': profile.level})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):
    profiles = UserProfile.objects.select_related('user').order_by('-xp', '-balance')
    result = []
    for p in profiles:
        # Calculate portfolio market value so net_worth = cash + holdings
        portfolio_value = sum(
            item.stock.current_price * item.quantity
            for item in Portfolio.objects.filter(user=p).select_related('stock')
        )
        net_worth = float(p.balance) + float(portfolio_value)
        result.append({
            'username':  p.user.username,
            'level':     p.level,
            'xp':        p.xp,
            'balance':   round(float(p.balance), 2),
            'net_worth': round(net_worth, 2),
        })
    return Response(result)

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
    if not username:
        return Response({'error': 'Not logged in. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        quantity = int(request.data.get('quantity', 0))
    except (ValueError, TypeError):
        return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity <= 0:
        return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock = Stock.objects.get(id=stock_id)
    except Stock.DoesNotExist:
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(user__username=username)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found. Please log in again.'}, status=status.HTTP_404_NOT_FOUND)

    total_cost = stock.current_price * quantity
    if profile.balance < total_cost:
        return Response({'error': f'Insufficient funds. Need Rs.{total_cost:.2f}, have Rs.{profile.balance:.2f}'}, status=status.HTTP_400_BAD_REQUEST)

    profile.balance -= total_cost
    profile.save()

    portfolio, created = Portfolio.objects.get_or_create(user=profile, stock=stock)
    old_total = portfolio.average_buy_price * portfolio.quantity
    portfolio.quantity += quantity
    portfolio.average_buy_price = (old_total + total_cost) / portfolio.quantity
    portfolio.save()

    return Response({'message': f'Bought {quantity} shares of {stock.symbol}', 'balance': float(profile.balance)})

@api_view(['POST'])
@permission_classes([AllowAny])
def sell_stock(request):
    username = request.data.get('username')
    stock_id = request.data.get('stock_id')
    if not username:
        return Response({'error': 'Not logged in. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        quantity = int(request.data.get('quantity', 0))
    except (ValueError, TypeError):
        return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity <= 0:
        return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock = Stock.objects.get(id=stock_id)
    except Stock.DoesNotExist:
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(user__username=username)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found. Please log in again.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        portfolio = Portfolio.objects.get(user=profile, stock=stock)
    except Portfolio.DoesNotExist:
        return Response({'error': f'You do not own any shares of {stock.symbol}'}, status=status.HTTP_400_BAD_REQUEST)

    if portfolio.quantity < quantity:
        return Response({'error': f'You only own {portfolio.quantity} shares of {stock.symbol}'}, status=status.HTTP_400_BAD_REQUEST)

    total_earning = stock.current_price * quantity
    cost_basis    = portfolio.average_buy_price * quantity
    profit        = total_earning - cost_basis

    profile.balance += total_earning
    if profit > 0:
        profile.xp += 10
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
        'message': f'Sold {quantity} shares of {stock.symbol}',
        'balance': float(profile.balance),
        'profit':  float(profit),
        'xp':      profile.xp
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_portfolio(request):
    username = request.GET.get('username')
    try:
        profile = UserProfile.objects.get(user__username=username)
    except UserProfile.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)
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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_scenarios(request):
    """Return ALL scenarios of a given type so the frontend can manage the queue."""
    scenario_type = request.GET.get('type', 'SCAM')
    scenarios = list(Scenario.objects.filter(type=scenario_type).values(
        'id', 'type', 'hint_type', 'title', 'description', 'xp_reward', 'penalty', 'explanation'
    ))
    if not scenarios:
        return Response({'error': 'No scenarios found for type: ' + scenario_type}, status=status.HTTP_404_NOT_FOUND)
    return Response(scenarios)

@api_view(['POST'])
@permission_classes([AllowAny])
def answer_scenario(request):
    username    = request.data.get('username')
    scenario_id = request.data.get('scenario_id')
    action      = request.data.get('action', '')

    if not username:
        return Response({'error': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
    if not action:
        return Response({'error': 'No action provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        scenario = Scenario.objects.get(id=scenario_id)
    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(user__username=username)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found. Please log in again.'}, status=status.HTTP_404_NOT_FOUND)

    is_correct = action.strip().upper() == scenario.correct_action.strip().upper()

    if is_correct:
        profile.xp += scenario.xp_reward
        msg = f'Correct! You answered this {scenario.type} question right.'
    else:
        profile.balance -= scenario.penalty
        msg = f'Wrong answer. You lost Rs.{float(scenario.penalty):.2f} from your balance.'

    if profile.xp >= profile.level * 100:
        profile.level += 1
        profile.xp   -= profile.level * 100

    profile.save()

    return Response({
        'correct':     is_correct,
        'message':     msg,
        'new_balance': float(profile.balance),
        'new_xp':      profile.xp,
        'new_level':   profile.level,
        'penalty':     float(scenario.penalty),
        'xp_reward':   scenario.xp_reward,
    })
