from django.urls import path
from .views import (
    register, user_login, get_profile, get_leaderboard, claim_mission_reward,
    get_stocks, buy_stock, sell_stock, get_portfolio,
    get_random_scenario, get_all_scenarios, answer_scenario
)

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', user_login, name='login'),
    
    path('user/profile/', get_profile, name='get_profile'),
    path('user/reward/', claim_mission_reward, name='claim_reward'),
    path('leaderboard/', get_leaderboard, name='leaderboard'),
    
    path('stocks/', get_stocks, name='get_stocks'),
    path('stocks/buy/', buy_stock, name='buy_stock'),
    path('stocks/sell/', sell_stock, name='sell_stock'),
    path('stocks/portfolio/', get_portfolio, name='get_portfolio'),
    
    path('scenarios/', get_random_scenario, name='get_scenario'),
    path('scenarios/all/', get_all_scenarios, name='get_all_scenarios'),
    path('scenarios/answer/', answer_scenario, name='answer_scenario'),
]
