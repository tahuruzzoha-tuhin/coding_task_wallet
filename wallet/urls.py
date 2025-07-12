from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/refresh/', views.refresh_token, name='refresh_token'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Wallet endpoints
    path('wallet/balance/', views.WalletBalanceView.as_view(), name='wallet_balance'),
    path('wallet/topup/', views.TopUpWalletView.as_view(), name='topup_wallet'),
    path('wallet/withdraw/', views.WithdrawFromWalletView.as_view(), name='withdraw_wallet'),
    
    # Transaction endpoints
    path('transactions/', views.TransactionHistoryView.as_view(), name='transaction_history'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
] 