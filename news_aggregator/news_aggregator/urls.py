from django.conf import settings
from django.conf.urls.static import static
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
    path('sports/', views.sports, name='sports'),
    path('politics/', views.politics, name='politics'),  # updated
    path('entertainment/', views.entertainment, name='entertainment'),  # updated
    path('profile/', views.profile, name='profile'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)







