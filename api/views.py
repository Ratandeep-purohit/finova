from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile, Stock, Portfolio, Scenario
from .serializers import UserProfileSerializer, StockSerializer, PortfolioSerializer, ScenarioSerializer
import random, urllib.request, urllib.parse, json
from decimal import Decimal

# ── MOCK YOUTUBE SEARCH FOR DEMO ──────────────────────────────────────────────
MOCK_YOUTUBE_VIDS = [
    {'id': 'p7HKvqRI_Bo', 'title': 'Stock Market For Beginners 2024', 'channel': 'Pranjal Kamra', 'desc': 'Complete guide to investing in Indian stock market for beginners.', 'tags': ['stock', 'market', 'invest', 'share', 'trading']},
    {'id': '86_tVBiMDEo', 'title': 'Stock Market Explained - Animation', 'channel': 'Practical Wisdom', 'desc': 'A simple animated explanation of how the stock market works.', 'tags': ['stock', 'market', 'animation', 'basics']},
    {'id': 'nPpASBFHFtQ', 'title': 'Income Tax Filing Explained', 'channel': 'CA Manish Kumar', 'desc': 'Learn how to file income tax return step by step in India.', 'tags': ['tax', 'income tax', 'itr', 'filing', 'return']},
    {'id': 'fhMT0cWaFPo', 'title': 'How to Save Tax in India under 80C', 'channel': 'Invest Aaj For Kal', 'desc': 'Practical guide to Section 80C deductions and reducing tax.', 'tags': ['tax', '80c', 'save tax', 'deductions']},
    {'id': '9-ZDyHbk-aM', 'title': 'How Scammers Steal Money via UPI', 'channel': 'Finology Legal', 'desc': 'Understanding UPI payment frauds and how to stay safe online.', 'tags': ['upi', 'scam', 'fraud', 'safety', 'pay']},
    {'id': 'EfBLbkFdnhE', 'title': 'RBI Official Cyber Fraud Awareness', 'channel': 'Reserve Bank of India', 'desc': 'Official guide on protecting your money from phishing and scams.', 'tags': ['upi', 'scam', 'fraud', 'rbi', 'safety']},
    {'id': '1P5b_Z3x_oA', 'title': 'Mutual Funds for Beginners', 'channel': 'Groww', 'desc': 'What are mutual funds? Complete guide to SIP and lump sum investing.', 'tags': ['mutual funds', 'stock', 'invest', 'sip']},
    {'id': 'Xn7KEdY_Ojw', 'title': 'Budget 2024 Highlights Explained', 'channel': 'CA Rachana Ranade', 'desc': 'Simplified explanation of the ongoing Indian Budget and what it means for you.', 'tags': ['budget', 'tax', 'finance', 'economy']},
]

def _get_mock_vids(query):
    q = query.lower()
    results = []
    for v in MOCK_YOUTUBE_VIDS:
        # Match if query words are in title, channel, or tags
        title = str(v['title']).lower()
        channel = str(v['channel']).lower()
        tags = v['tags']
        if any(word in title or word in channel or word in tags for word in q.split()):
            results.append({
                'id': v['id'],
                'title': v['title'],
                'channel': v['channel'],
                'thumbnail': f"https://img.youtube.com/vi/{v['id']}/mqdefault.jpg",
                'desc': v['desc']
            })
    # If no exact match, return top 3 randomly to simulate algo
    if not results:
        results = random.sample(MOCK_YOUTUBE_VIDS, 3)
    return results

# ── YouTube Video Search ──────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_youtube(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)

    api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
    if not api_key or api_key == 'YOUR_YOUTUBE_API_KEY_HERE':
        # MOCK MODE FOR HACKATHON
        return Response(_get_mock_vids(query))

    safe_query = urllib.parse.quote(query + ' finance India education')
    url = (f"https://www.googleapis.com/youtube/v3/search"
           f"?part=snippet&q={safe_query}&type=video"
           f"&maxResults=8&videoEmbeddable=true&safeSearch=strict"
           f"&key={api_key}")
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        videos = []
        for item in data.get('items', []):
            vid_id = item['id'].get('videoId')
            sn = item['snippet']
            videos.append({
                'id': vid_id,
                'title': sn['title'],
                'channel': sn['channelTitle'],
                'thumbnail': sn['thumbnails'].get('medium', {}).get('url', ''),
                'desc': sn.get('description', '')[:120],
            })
        return Response(videos)
    except Exception as e:
        # Fallback to mock on timeout or API error
        return Response(_get_mock_vids(query))

# ── Tax Chatbot ──────────────────────────────────────────────────────────────
TAX_KB = [
    (['what is income tax', 'income tax kya'],
     "Income Tax is a direct tax levied by the Government of India on your annual income. "
     "If your income exceeds the basic exemption limit (₹2.5L old regime / ₹3L new regime), you must pay tax on the excess."),
    (['tax slab', 'tax rate', 'how much tax'],
     "Old Regime Slabs:\n• Up to ₹2.5L → 0%\n• ₹2.5L–5L → 5%\n• ₹5L–10L → 20%\n• Above ₹10L → 30%\n\n"
     "New Regime (2024-25):\n• Up to ₹3L → 0%\n• ₹3L–7L → 5%\n• ₹7L–10L → 10%\n• ₹10L–12L → 15%\n• ₹12L–15L → 20%\n• Above ₹15L → 30%"),
    (['80c', 'section 80c', 'ppf', 'elss', 'save tax'],
     "Section 80C lets you claim deductions up to ₹1.5 Lakh per year by investing in:\n"
     "• PPF (Public Provident Fund)\n• ELSS Mutual Funds\n• Life Insurance Premium\n• EPF / Employee Provident Fund\n• NSC (National Savings Certificate)\n• Tuition fees for children"),
    (['80d', 'health insurance', 'medical'],
     "Section 80D allows deductions on health insurance premiums:\n"
     "• Self + Family: up to ₹25,000\n• If parents are senior citizens: +₹50,000 extra\n• Preventive health check-up: ₹5,000 (within above limits)"),
    (['nps', '80ccd', 'pension'],
     "Section 80CCD(1B) allows an ADDITIONAL ₹50,000 deduction for NPS (National Pension System) contributions — "
     "over and above your ₹1.5L 80C limit. So combined you can save on ₹2L of income tax!"),
    (['hra', 'house rent', 'rent allowance'],
     "HRA (House Rent Allowance) is exempt from tax if you live in rented accommodation. "
     "The exemption is the LEAST of:\n• Actual HRA received\n• 50% of salary (metro) / 40% (non-metro)\n• Actual rent paid minus 10% of salary"),
    (['standard deduction'],
     "The Standard Deduction of ₹50,000 is automatically given to all salaried employees and pensioners "
     "without needing any proof or investment. It reduces your taxable income by ₹50,000 directly."),
    (['tds', 'tax deducted at source'],
     "TDS (Tax Deducted at Source) is tax deducted by your employer before giving you your salary. "
     "Your Form 16 shows the TDS details. If too much TDS was deducted, you get a refund when filing ITR."),
    (['itr', 'file return', 'income tax return', 'how to file'],
     "ITR (Income Tax Return) must be filed by July 31 every year for the previous financial year. "
     "Steps:\n1. Collect Form 16 from employer\n2. Login to incometax.gov.in\n3. Choose correct ITR form (ITR-1 for salaried)\n4. Auto-fill using AIS/Form 26AS\n5. Verify using Aadhaar OTP"),
    (['capital gain', 'stocks profit', 'mutual fund profit'],
     "Capital Gains Tax applies on profits from selling stocks/mutual funds:\n"
     "• Short Term Capital Gain (STCG): Held < 1 year → taxed at 15%\n"
     "• Long Term Capital Gain (LTCG): Held > 1 year → 10% on gains above ₹1 Lakh per year (no indexation)"),
    (['old regime', 'new regime', 'which is better', 'which regime'],
     "Old vs New Regime:\n"
     "• Old Regime: Higher tax rates BUT you can claim deductions (80C, HRA, etc.) to reduce taxable income\n"
     "• New Regime: Lower tax rates but NO deductions allowed\n"
     "Rule of thumb: If your total deductions cross ₹3.75L, Old Regime is better. Otherwise New Regime saves more."),
    (['pan', 'pan card'],
     "PAN (Permanent Account Number) is a 10-character alphanumeric ID issued by the Income Tax department. "
     "It is mandatory for:\n• Filing income tax returns\n• Opening a bank account\n• Transactions above ₹50,000\n• Buying/selling property"),
    (['ais', 'form 26as', 'annual information'],
     "AIS (Annual Information Statement) is a detailed record of all your financial transactions reported to the Income Tax dept — "
     "including salary, bank interest, dividends, and property sales. Always cross-check AIS before filing your ITR."),
    (['gst', 'goods and services tax'],
     "GST (Goods and Services Tax) is an indirect tax on goods and services — different from Income Tax. "
     "GST Slabs: 0% (essentials), 5% (basic goods), 12%, 18% (most services), 28% (luxury). "
     "For a Finova student, know that GST applies on your phone bill, restaurant food, and clothing."),
    (['home loan', 'section 24', 'housing loan'],
     "Section 24(b) allows you to deduct interest paid on home loans up to ₹2 Lakh per year from your taxable income. "
     "This is IN ADDITION to your Section 80C deductions — helping you save significantly if you have a home loan."),
]

def _tax_answer(question):
    q = question.lower()
    
    # Check for conversational openers
    if any(k in q for k in ['hi', 'hello', 'hey', 'who are you']):
        return "Hello! I am the Finova Tax Assistant. I'm here to help you understand Indian income tax, deductions, slabs, and anything else you'd like to ask. What's your tax question?"
        
    for keywords, answer in TAX_KB:
        # Check if any keyword matches as a substring
        if any(k in q for k in keywords):
            return "Based on your question, here is what you need to know:\n\n" + answer + "\n\nDoes this help clarify your situation?"
    
    # Conversational ChatGPT-style fallback
    return (
        f"I understand you're asking about '{question}'. "
        "As an AI learning about Indian taxation, I might not have the precise calculations for that exact situation right now.\n\n"
        "However, I recommend checking how this applies against the general tax exemptions (like Section 80C) or the new tax regime slabs. "
        "Could you try asking specifically about deductions, tax slabs, ITR filing, or capital gains so I can give you a concrete rule?"
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def tax_chat(request):
    question = request.data.get('question', '').strip()
    if not question:
        return Response({'error': 'Question required'}, status=400)
    answer = _tax_answer(question)
    return Response({'answer': answer})

# ── UPI Open-ended Answer Evaluation ─────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_upi_text(request):
    """Evaluate a free-text answer against a UPI scenario."""
    username    = request.data.get('username')
    scenario_id = request.data.get('scenario_id')
    user_text   = request.data.get('text', '').strip().lower()

    try:
        scenario = Scenario.objects.get(id=scenario_id)
    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found'}, status=404)

    # Determine correct answer
    is_scam     = scenario.correct_action == 'DECLINE'
    safe_kw     = ['safe', 'pay', 'genuine', 'real', 'legit', 'ok', 'proceed', 'trust']
    scam_kw     = ['scam', 'fraud', 'fake', 'decline', 'block', 'report', 'no', 'suspicious', 'phishing', 'danger']

    safe_score  = sum(1 for k in safe_kw  if k in user_text)
    scam_score  = sum(1 for k in scam_kw  if k in user_text)

    if scam_score == 0 and safe_score == 0:
        return Response({'error': 'Please write more detail about whether the message is safe or a scam.'}, status=200)

    user_thinks_scam = scam_score >= safe_score
    correct = (is_scam == user_thinks_scam)

    try:
        profile = UserProfile.objects.get(user__username=username)
        if correct:
            profile.xp += scenario.xp_reward
            profile.level = max(1, (profile.xp // 500) + 1)
            profile.save()
            return Response({
                'correct': True,
                'xp_reward': scenario.xp_reward,
                'message': 'Great instinct! You correctly identified this scenario.',
                'explanation': scenario.explanation,
                'xp': profile.xp,
                'balance': float(profile.balance),
            })
        else:
            penalty = scenario.penalty
            profile.balance = max(Decimal('0'), profile.balance - penalty)
            profile.save()
            return Response({
                'correct': False,
                'penalty': float(penalty),
                'message': 'Not quite right. Study the explanation below.',
                'explanation': scenario.explanation,
                'xp': profile.xp,
                'balance': float(profile.balance),
            })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


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

@api_view(['POST'])
@permission_classes([AllowAny])
def convert_xp(request):
    """Convert XP to virtual money. Rate: 10 XP = Rs.100 (Rs.10 per XP)."""
    username   = request.data.get('username')
    xp_to_use  = int(request.data.get('xp_amount', 0))

    if xp_to_use <= 0:
        return Response({'error': 'Invalid XP amount'}, status=status.HTTP_400_BAD_REQUEST)
    if xp_to_use % 10 != 0:
        return Response({'error': 'XP must be in multiples of 10'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = UserProfile.objects.get(user__username=username)

        if profile.xp < xp_to_use:
            return Response({'error': f'Not enough XP. You have {profile.xp} XP.'}, status=status.HTTP_400_BAD_REQUEST)

        money_gained = Decimal(str(xp_to_use * 10))   # 1 XP = Rs.10
        profile.xp      -= xp_to_use
        profile.balance += money_gained

        # Recalculate level after XP deduction
        profile.level = max(1, (profile.xp // 500) + 1)
        profile.save()

        return Response({
            'message': f'Converted {xp_to_use} XP → Rs.{money_gained}',
            'xp':      profile.xp,
            'balance': float(profile.balance),
            'level':   profile.level,
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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
            'balance':   float(p.balance),
            'net_worth': float(net_worth),
        })
    return Response(result)

@api_view(['GET'])
def get_stocks(request):
    # Simulate price fluctuation on fetch for demo
    for stock in Stock.objects.all():
        change_pct = random.uniform(float(-stock.volatility), float(stock.volatility))
        change_amount = float(stock.current_price) * (change_pct / 100.0)
        stock.current_price = max(Decimal('1.00'), stock.current_price + Decimal(f"{change_amount:.2f}"))
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
