import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Finova.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile

print("Creating dummy users for leaderboard...")

names = ['HustlerZero', 'WallStreetWhiz', 'DiamondHands', 'CryptoKing', 'FinanceBro']

for name in names:
    user, created = User.objects.get_or_create(username=name)
    if created:
        user.set_password('password123')
        user.save()
        profile, p_created = UserProfile.objects.get_or_create(user=user)
        # Give them random stats for the leaderboard
        profile.xp = random.randint(100, 1500)
        profile.level = int(profile.xp / 100) + 1
        profile.balance = float(10000 + random.randint(-5000, 20000))
        profile.save()

print("Dummy users populated.")
