import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Finova.settings')
django.setup()

from api.models import Stock, Scenario

print("Populating database...")

# Setup Stocks
stocks_data = [
    {'symbol': 'TATAM', 'name': 'Tata Motors Fake', 'current_price': 150.00, 'volatility': 5.0},
    {'symbol': 'RLNC', 'name': 'Reliance Fake', 'current_price': 2500.00, 'volatility': 2.5},
    {'symbol': 'INFY', 'name': 'Infosys Fake', 'current_price': 1400.00, 'volatility': 3.0},
    {'symbol': 'HDFC', 'name': 'HDFC Bank Fake', 'current_price': 1600.00, 'volatility': 1.5},
    {'symbol': 'ZMATO', 'name': 'Zomato Fake', 'current_price': 90.00, 'volatility': 8.0},
]

for sd in stocks_data:
    Stock.objects.get_or_create(symbol=sd['symbol'], defaults=sd)
print("Stocks populated.")

# Setup Scenarios
scenarios_data = [
    {
        'type': 'SCAM',
        'title': 'You won a iPhone 15!',
        'description': 'A message from a random number says you won an iPhone and need to pay ₹100 for delivery by clicking the link.',
        'correct_action': 'DECLINE',
        'xp_reward': 50,
        'penalty': 1000.00
    },
    {
        'type': 'SCAM',
        'title': 'Urgent Money Request',
        'description': 'Your friend messages you on Telegram asking for ₹2000 immediately for a medical emergency.',
        'correct_action': 'DECLINE', # Or REPORT
        'xp_reward': 50,
        'penalty': 2000.00   
    },
    {
        'type': 'TAX',
        'title': 'Freelance Income',
        'description': 'You earned ₹50,000 from freelancing this month. Do you need to declare it?',
        'correct_action': 'YES',
        'xp_reward': 100,
        'penalty': 500.00
    }
]

for sc in scenarios_data:
    Scenario.objects.get_or_create(title=sc['title'], defaults=sc)
print("Scenarios populated.")
print("Done!")
