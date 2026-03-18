from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    
    # Frontend Views
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('dashboard.html', TemplateView.as_view(template_name='dashboard.html')),
    path('stock_market.html', TemplateView.as_view(template_name='stock_market.html')),
    path('scams.html', TemplateView.as_view(template_name='scams.html')),
]
