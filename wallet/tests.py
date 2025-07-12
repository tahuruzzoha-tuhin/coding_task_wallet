from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
import json

from .models import Wallet, Transaction

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class WalletModelTest(TestCase):
    """Test cases for Wallet model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
    
    def test_wallet_creation(self):
        self.assertEqual(self.wallet.balance, Decimal('100.00'))
        self.assertEqual(self.wallet.currency, 'USD')
        self.assertTrue(self.wallet.is_active)
    
    def test_wallet_deposit(self):
        initial_balance = self.wallet.balance
        deposit_amount = Decimal('50.00')
        self.wallet.deposit(deposit_amount)
        self.assertEqual(self.wallet.balance, initial_balance + deposit_amount)
    
    def test_wallet_withdrawal(self):
        initial_balance = self.wallet.balance
        withdrawal_amount = Decimal('30.00')
        self.wallet.withdraw(withdrawal_amount)
        self.assertEqual(self.wallet.balance, initial_balance - withdrawal_amount)
    
    def test_wallet_insufficient_balance(self):
        with self.assertRaises(ValueError):
            self.wallet.withdraw(Decimal('150.00'))
    
    def test_wallet_negative_deposit(self):
        with self.assertRaises(ValueError):
            self.wallet.deposit(Decimal('-10.00'))
    
    def test_wallet_negative_withdrawal(self):
        with self.assertRaises(ValueError):
            self.wallet.withdraw(Decimal('-10.00'))


class TransactionModelTest(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
    
    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type='DEPOSIT',
            amount=Decimal('50.00'),
            status='COMPLETED',
            balance_before=Decimal('100.00'),
            balance_after=Decimal('150.00')
        )
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertTrue(transaction.reference.startswith('TXN-'))
    
    def test_transaction_reference_generation(self):
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type='WITHDRAWAL',
            amount=Decimal('20.00'),
            status='COMPLETED',
            balance_before=Decimal('100.00'),
            balance_after=Decimal('80.00')
        )
        self.assertTrue(transaction.reference.startswith('TXN-'))
        self.assertEqual(len(transaction.reference), 12)  # TXN- + 8 chars


class WalletAPITest(APITestCase):
    """Test cases for Wallet API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
    
    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('wallet:health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('wallet:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        
        # Check if wallet was created
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(hasattr(user, 'wallet'))
    
    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse('wallet:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_wallet_balance_authenticated(self):
        """Test wallet balance endpoint with authentication"""
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:wallet_balance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '100.00')
    
    def test_wallet_balance_unauthenticated(self):
        """Test wallet balance endpoint without authentication"""
        url = reverse('wallet:wallet_balance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_topup_wallet(self):
        """Test wallet top-up endpoint"""
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:topup_wallet')
        data = {
            'amount': '50.00',
            'currency': 'USD',
            'description': 'Test top-up'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['new_balance']), '150.00')
        
        # Check if transaction was created
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('150.00'))
        self.assertEqual(self.wallet.transactions.count(), 1)
    
    def test_withdraw_wallet(self):
        """Test wallet withdrawal endpoint"""
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:withdraw_wallet')
        data = {
            'amount': '30.00',
            'description': 'Test withdrawal'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['new_balance']), '70.00')
        
        # Check if transaction was created
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('70.00'))
        self.assertEqual(self.wallet.transactions.count(), 1)
    
    def test_withdraw_insufficient_balance(self):
        """Test withdrawal with insufficient balance"""
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:withdraw_wallet')
        data = {
            'amount': '150.00',
            'description': 'Test withdrawal'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient balance', response.data['error'])
    
    def test_transaction_history(self):
        """Test transaction history endpoint"""
        # Create some transactions
        Transaction.objects.create(
            wallet=self.wallet,
            transaction_type='DEPOSIT',
            amount=Decimal('50.00'),
            status='COMPLETED',
            balance_before=Decimal('100.00'),
            balance_after=Decimal('150.00')
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:transaction_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_user_profile(self):
        """Test user profile endpoint"""
        self.client.force_authenticate(user=self.user)
        url = reverse('wallet:profile')
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        
        # Test PUT
        data = {'first_name': 'Updated'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')


class SerializerTest(TestCase):
    """Test cases for serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
    
    def test_user_registration_serializer(self):
        """Test user registration serializer"""
        from .serializers import UserRegistrationSerializer
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(hasattr(user, 'wallet'))
    
    def test_user_registration_serializer_password_mismatch(self):
        """Test user registration serializer with password mismatch"""
        from .serializers import UserRegistrationSerializer
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_wallet_serializer(self):
        """Test wallet serializer"""
        from .serializers import WalletSerializer
        
        serializer = WalletSerializer(self.wallet)
        data = serializer.data
        
        self.assertEqual(data['balance'], '100.00')
        self.assertEqual(data['currency'], 'USD')
        self.assertTrue(data['is_active'])
        self.assertIn('user', data)
