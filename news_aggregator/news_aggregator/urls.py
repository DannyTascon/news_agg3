from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from aggregator import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('fetch-data/<str:category>/', views.fetch_news_data, name='fetch_data'),  # updated
    path('accounts/profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('sources/', views.sources, name='sources'),
    path('shopping/', views.shopping, name='shopping'),
    path('politics/', views.politics, name='politics'),  # updated
    path('entertainment/', views.entertainment, name='entertainment'),  # updated
]







