from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Transaction


@shared_task
def cleanup_old_transactions():
    """Clean up old failed transactions (older than 30 days)"""
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = Transaction.objects.filter(
        status='FAILED',
        created_at__lt=cutoff_date
    ).delete()
    
    return f"Deleted {deleted_count} old failed transactions"


@shared_task
def process_transaction_notification(transaction_id):
    """Process transaction notification (placeholder for future implementation)"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Here you would implement notification logic
        # e.g., send email, push notification, etc.
        print(f"Processing notification for transaction: {transaction.reference}")
        return f"Notification processed for transaction {transaction.reference}"
    except Transaction.DoesNotExist:
        return f"Transaction {transaction_id} not found"


@shared_task
def generate_monthly_statement(user_id, year, month):
    """Generate monthly statement for a user"""
    from .models import User
    from django.db.models import Sum
    
    try:
        user = User.objects.get(id=user_id)
        wallet = user.wallet
        
        # Get transactions for the specified month
        start_date = timezone.datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = timezone.datetime(year, month + 1, 1, tzinfo=timezone.utc)
        
        transactions = Transaction.objects.filter(
            wallet=wallet,
            created_at__gte=start_date,
            created_at__lt=end_date,
            status='COMPLETED'
        )
        
        # Calculate totals
        total_deposits = transactions.filter(transaction_type='DEPOSIT').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_withdrawals = transactions.filter(transaction_type='WITHDRAWAL').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        statement_data = {
            'user': user.email,
            'month': f"{year}-{month:02d}",
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'net_change': total_deposits - total_withdrawals,
            'transaction_count': transactions.count(),
            'ending_balance': wallet.balance
        }
        
        # Here you would save or send the statement
        print(f"Generated statement for {user.email}: {statement_data}")
        return statement_data
        
    except User.DoesNotExist:
        return f"User {user_id} not found" 