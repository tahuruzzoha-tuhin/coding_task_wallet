from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import User, Wallet, Transaction
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    WalletSerializer, TransactionSerializer, TopUpSerializer,
    WithdrawalSerializer, TransactionListSerializer
)
from drf_yasg.utils import swagger_auto_schema


class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({"status": "healthy", "message": "Wallet API is running"}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """User profile endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletBalanceView(APIView):
    """Get wallet balance endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            wallet = request.user.wallet
            serializer = WalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            # Create wallet if it doesn't exist
            wallet = Wallet.objects.create(user=request.user)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)


class TopUpWalletView(APIView):
    """Top up wallet endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                wallet = request.user.wallet
                amount = serializer.validated_data['amount']
                currency = serializer.validated_data['currency']
                description = serializer.validated_data.get('description', 'Wallet top-up')
                
                # Check if currency matches wallet currency
                if wallet.currency != currency:
                    return Response({
                        'error': f'Currency mismatch. Wallet currency is {wallet.currency}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Record balance before transaction
                balance_before = wallet.balance
                
                # Perform deposit
                wallet.deposit(amount)
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    currency=currency,
                    status='COMPLETED',
                    description=description,
                    balance_before=balance_before,
                    balance_after=wallet.balance
                )
                
                return Response({
                    'message': 'Wallet topped up successfully',
                    'transaction': TransactionSerializer(transaction_obj).data,
                    'new_balance': wallet.balance
                }, status=status.HTTP_200_OK)
                
            except Wallet.DoesNotExist:
                # Create wallet if it doesn't exist
                wallet = Wallet.objects.create(user=request.user, currency=currency)
                balance_before = Decimal('0.00')
                wallet.deposit(amount)
                
                transaction_obj = Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    currency=currency,
                    status='COMPLETED',
                    description=description,
                    balance_before=balance_before,
                    balance_after=wallet.balance
                )
                
                return Response({
                    'message': 'Wallet created and topped up successfully',
                    'transaction': TransactionSerializer(transaction_obj).data,
                    'new_balance': wallet.balance
                }, status=status.HTTP_201_CREATED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawFromWalletView(APIView):
    """Withdraw from wallet endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            try:
                wallet = request.user.wallet
                amount = serializer.validated_data['amount']
                description = serializer.validated_data.get('description', 'Wallet withdrawal')
                
                # Check if wallet has sufficient balance
                if not wallet.can_withdraw(amount):
                    return Response({
                        'error': 'Insufficient balance',
                        'current_balance': wallet.balance,
                        'requested_amount': amount
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Record balance before transaction
                balance_before = wallet.balance
                
                # Perform withdrawal
                wallet.withdraw(amount)
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='WITHDRAWAL',
                    amount=amount,
                    currency=wallet.currency,
                    status='COMPLETED',
                    description=description,
                    balance_before=balance_before,
                    balance_after=wallet.balance
                )
                
                return Response({
                    'message': 'Withdrawal successful',
                    'transaction': TransactionSerializer(transaction_obj).data,
                    'new_balance': wallet.balance
                }, status=status.HTTP_200_OK)
                
            except Wallet.DoesNotExist:
                return Response({
                    'error': 'Wallet not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryView(generics.ListAPIView):
    """List transaction history endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionListSerializer
    
    def get_queryset(self):
        try:
            wallet = self.request.user.wallet
            return Transaction.objects.filter(wallet=wallet)
        except Wallet.DoesNotExist:
            return Transaction.objects.none()


class TransactionDetailView(generics.RetrieveAPIView):
    """Get transaction detail endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        try:
            wallet = self.request.user.wallet
            return Transaction.objects.filter(wallet=wallet)
        except Wallet.DoesNotExist:
            return Transaction.objects.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_token(request):
    """Refresh JWT token endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
