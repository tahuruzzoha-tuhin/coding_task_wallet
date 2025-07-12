# 🔐 Secure Wallet API

A robust and secure wallet API built with Django REST Framework, featuring JWT authentication, PostgreSQL database, Redis caching, and comprehensive transaction management.

## 🚀 Features

- **🔐 JWT Authentication**: Secure user registration and login with JWT tokens
- **💰 Wallet Management**: Create, view, and manage user wallets
- **💳 Transaction Processing**: Deposit, withdraw, and track transaction history
- **📊 Real-time Balance**: Get current wallet balance with transaction tracking
- **🔒 Security**: Password validation, transaction atomicity, and proper error handling
- **📚 API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **🧪 Comprehensive Testing**: Unit tests with pytest and coverage reporting
- **🐳 Docker Support**: Complete containerization with docker-compose
- **⚡ Background Tasks**: Celery integration for async processing
- **📈 Monitoring**: Health check endpoints and logging

## 🛠 Tech Stack

- **Backend**: Django 5.2.4 + Django REST Framework
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Testing**: pytest + pytest-django
- **Containerization**: Docker + docker-compose
- **Background Tasks**: Celery

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## 🚀 Quick Start

### Section 1: Dockerized Setup (Recommended)

**Prerequisites:**
- Docker and Docker Compose

**Steps:**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coding_task
   ```

2. **Start all services**
   ```bash
   docker network create common.network
   docker compose up --build

   or

   docker compose up --build -d  # For running in the background .
   ```

3. **Run migrations**
   ```bash
   docker compose exec wallet.task.backend python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   docker compose exec wallet.task.backend python manage.py createsuperuser
   ```

5. **Access the API**
   - API Base URL: http://localhost:8000/api/v1/
   - Swagger Documentation: http://localhost:8000/swagger/
   - Admin Interface: http://localhost:8000/admin/

6. **Using JWT Authentication in Swagger**
   - After running the project, register a user using the `/api/v1/auth/register/` endpoint
   - Then login the user using `/api/v1/auth/login/` endpoint
   - Copy the access token from the response
   - In Swagger UI, click the "Authorize" button (lock icon)
   - Set the token as `Bearer <your_access_token>` (include "Bearer " prefix)
   - Click "Authorize" to save
   - Now you will be able to execute all authenticated routes

**Useful Docker Commands:**
```bash
   # View logs
   docker compose logs -f

   # Stop services
   docker compose down

   # Restart services
   docker compose restart

   # Run tests
   docker compose exec wallet.task.backend python -m pytest wallet/tests.py -v

   # Access Django shell
   docker compose exec wallet.task.backend python manage.py shell

   # Access database
   docker compose exec wallet.task.db psql -U wallet_user -d wallet_db

   # Access Redis CLI
   docker compose exec wallet.task.redis redis-cli
```

---

### Section 2: Local Development (Without Docker)

**Prerequisites:**
- Python 3.11+
- Virtual environment (recommended)

**Steps:**

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   DJANGO_SETTINGS_MODULE=mysite.local_settings python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   DJANGO_SETTINGS_MODULE=mysite.local_settings python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   DJANGO_SETTINGS_MODULE=mysite.local_settings python manage.py runserver
   ```

6. **Access the API**
   - API Base URL: http://localhost:8000/api/v1/
   - Swagger Documentation: http://localhost:8000/swagger/
   - Admin Interface: http://localhost:8000/admin/

7. **Using JWT Authentication in Swagger**
   - After running the project, register a user using the `/api/v1/auth/register/` endpoint
   - Then login the user using `/api/v1/auth/login/` endpoint
   - Copy the access token from the response
   - In Swagger UI, click the "Authorize" button (lock icon)
   - Set the token as `Bearer <your_access_token>` (include "Bearer " prefix)
   - Click "Authorize" to save
   - Now you will be able to execute all authenticated routes

**Local Development Features:**
- ✅ Uses SQLite database (no PostgreSQL needed)
- ✅ Disables Redis/Celery (no Redis needed)
- ✅ No environment variables required
- ✅ Simple setup and run

**Useful Local Commands:**
```bash
# Run tests
DJANGO_SETTINGS_MODULE=mysite.local_settings pytest

# Access Django shell
DJANGO_SETTINGS_MODULE=mysite.local_settings python manage.py shell

# Create migrations
DJANGO_SETTINGS_MODULE=mysite.local_settings python manage.py makemigrations
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "username": "tahuruzzoha_tuhin",
    "email": "tahuruzzoha@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "tahuruzzoha",
    "last_name": "tuhin"
}
```

#### Login User
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "tahuruzzoha@example.com",
    "password": "securepass123"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token_here"
}
```

### Wallet Endpoints

#### Get Wallet Balance
```http
GET /api/v1/wallet/balance/
Authorization: Bearer your_access_token_here
```

#### Top Up Wallet
```http
POST /api/v1/wallet/topup/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
    "amount": "100.00",
    "currency": "USD",
    "description": "Monthly salary deposit"
}
```

#### Withdraw from Wallet
```http
POST /api/v1/wallet/withdraw/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
    "amount": "50.00",
    "description": "Shopping expenses"
}
```

### Transaction Endpoints

#### Get Transaction History
```http
GET /api/v1/transactions/
Authorization: Bearer your_access_token_here
```

#### Get Transaction Detail
```http
GET /api/v1/transactions/{transaction_id}/
Authorization: Bearer your_access_token_here
```

### User Profile

#### Get User Profile
```http
GET /api/v1/profile/
Authorization: Bearer your_access_token_here
```

#### Update User Profile
```http
PUT /api/v1/profile/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
    "first_name": "tahuruzzoha",
    "last_name": "tuhin",
    "phone_number": "+1234567890"
}
```

## 🧪 Running Tests

### Using Docker
```bash
docker compose exec web pytest wallet/tests.py -v
```

### Local Development
```bash
DJANGO_SETTINGS_MODULE=mysite.local_settings pytest wallet/tests.py -v
```

### With Coverage
```bash
# Docker
docker compose exec web pytest --cov=wallet --cov-report=html

# Local
DJANGO_SETTINGS_MODULE=mysite.local_settings pytest --cov=wallet --cov-report=html
```

## 📊 Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `username` (VARCHAR)
- `email` (VARCHAR, Unique)
- `password` (VARCHAR, Hashed)
- `first_name` (VARCHAR)
- `last_name` (VARCHAR)
- `phone_number` (VARCHAR, Optional)
- `date_of_birth` (DATE, Optional)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Wallets Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `balance` (DECIMAL)
- `currency` (VARCHAR, Choices: USD, EUR, GBP, JPY)
- `is_active` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Transactions Table
- `id` (UUID, Primary Key)
- `wallet_id` (UUID, Foreign Key)
- `transaction_type` (VARCHAR, Choices: DEPOSIT, WITHDRAWAL, TRANSFER)
- `amount` (DECIMAL)
- `currency` (VARCHAR)
- `status` (VARCHAR, Choices: PENDING, COMPLETED, FAILED, CANCELLED)
- `description` (TEXT)
- `reference` (VARCHAR, Unique)
- `balance_before` (DECIMAL)
- `balance_after` (DECIMAL)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `POSTGRES_DB` | Database name | `wallet_db` |
| `POSTGRES_USER` | Database user | `wallet_user` |
| `POSTGRES_PASSWORD` | Database password | `wallet_password` |
| `POSTGRES_HOST` | Database host | `localhost` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### JWT Configuration

- Access Token Lifetime: 60 minutes
- Refresh Token Lifetime: 1 day
- Algorithm: HS256

## 🚀 Deployment

### Production Considerations

1. **Security**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Enable HTTPS

2. **Database**
   - Use production PostgreSQL instance
   - Configure connection pooling
   - Set up regular backups

3. **Caching**
   - Configure Redis for production
   - Set up Redis persistence

4. **Monitoring**
   - Set up logging aggregation
   - Configure health checks
   - Monitor application metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.

## 🔄 API Versioning

The API uses URL versioning (v1). Future versions will be available at `/api/v2/`, etc.

## 📈 Performance

- Database queries are optimized with select_related
- Redis caching for frequently accessed data
- Pagination for large result sets
- Background task processing with Celery

## 🔒 Security Features

- JWT token-based authentication
- Password validation and hashing
- Transaction atomicity
- Input validation and sanitization
- CORS configuration
- Rate limiting (can be added)
- SQL injection protection
- XSS protection

## 🧰 Postman Collection

A ready-to-use Postman collection is provided for quick API testing.

- [Download wallet_api.postman_collection.json](./wallet_api.postman_collection.json)

### How to Use

1. **Import the Collection**
   - Open Postman.
   - Click **Import**.
   - Select `wallet_api.postman_collection.json` from the project root.

2. **Set Environment Variables**
   - Configure variables like `base_url` and `access_token` in Postman.

3. **Test Endpoints**
   - All major endpoints are pre-configured for easy testing.

---

**Tip:** The collection covers all endpoints described above. You can duplicate or modify requests as needed.