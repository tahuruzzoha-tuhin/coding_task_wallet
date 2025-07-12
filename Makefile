.PHONY: help install test run build up down migrate superuser shell clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=wallet --cov-report=html --cov-report=term-missing

run: ## Run development server
	python manage.py runserver

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

migrate: ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations: ## Create database migrations
	docker-compose exec web python manage.py makemigrations

superuser: ## Create superuser
	docker-compose exec web python manage.py createsuperuser

shell: ## Open Django shell
	docker-compose exec web python manage.py shell

collectstatic: ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

clean: ## Clean up Docker containers and volumes
	docker-compose down -v
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

status: ## Show service status
	docker-compose ps

# Development shortcuts
dev: up migrate ## Start development environment
	@echo "Development environment started!"
	@echo "API: http://localhost:8000/api/v1/"
	@echo "Swagger: http://localhost:8000/swagger/"
	@echo "Admin: http://localhost:8000/admin/"

# Production-like commands
prod-build: ## Build for production
	docker-compose -f docker-compose.yml build --no-cache

prod-up: ## Start production services
	docker-compose -f docker-compose.yml up -d

# Database commands
db-backup: ## Backup database
	docker-compose exec db pg_dump -U wallet_user wallet_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	docker-compose exec -T db psql -U wallet_user wallet_db < $(FILE)

# Celery commands
celery-worker: ## Start Celery worker
	docker-compose exec web celery -A mysite worker -l info

celery-beat: ## Start Celery beat scheduler
	docker-compose exec web celery -A mysite beat -l info

# Security commands
check-security: ## Run security checks
	docker-compose exec web python manage.py check --deploy
	docker-compose exec web bandit -r wallet/

# Performance commands
profile: ## Run performance profiling
	docker-compose exec web python -m cProfile -o profile.stats manage.py runserver

# Documentation commands
docs: ## Generate API documentation
	docker-compose exec web python manage.py spectacular --file schema.yml

# Linting and formatting
lint: ## Run code linting
	docker-compose exec web flake8 wallet/
	docker-compose exec web black --check wallet/
	docker-compose exec web isort --check-only wallet/

format: ## Format code
	docker-compose exec web black wallet/
	docker-compose exec web isort wallet/ 