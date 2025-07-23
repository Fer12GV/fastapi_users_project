#!/bin/bash

# =============================================================================
# FastAPI Users Project - Deployment Script
# =============================================================================
# Usage: ./scripts/deploy.sh [environment]
# Environments: local, docker, production, aws

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        print_error "pip is not installed"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Function to deploy locally
deploy_local() {
    print_status "Deploying to local environment..."
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.local .env
        print_status "Copied .env.local to .env"
    fi
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    
    # Run database migrations (if using Alembic)
    if [ -f alembic.ini ]; then
        print_status "Running database migrations..."
        alembic upgrade head
    fi
    
    # Start the application
    print_success "Starting application locally..."
    echo "Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
}

# Function to deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Copy environment file
    cp .env.docker .env
    print_status "Using Docker environment configuration"
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose down --remove-orphans
    docker-compose up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Application is running successfully!"
        echo "API Documentation: http://localhost:8000/docs"
        echo "Health Check: http://localhost:8000/health"
        echo "View logs: docker-compose logs -f"
    else
        print_error "Application failed to start properly"
        echo "Check logs: docker-compose logs"
        exit 1
    fi
}

# Function to deploy to production
deploy_production() {
    print_status "Deploying to production..."
    print_warning "Make sure you have configured .env.production with secure values!"
    
    # Copy production environment file
    if [ ! -f .env.production ]; then
        print_error ".env.production file not found. Please create it from .env.example"
        exit 1
    fi
    
    cp .env.production .env
    print_status "Using production environment configuration"
    
    # Validate critical environment variables
    source .env
    if [ "$SECRET_KEY" = "CHANGE_THIS_SUPER_SECRET_KEY_MINIMUM_32_CHARACTERS_FOR_PRODUCTION_USE" ]; then
        print_error "SECRET_KEY must be changed in production!"
        exit 1
    fi
    
    if [ "$DB_PASSWORD" = "CHANGE_THIS_SUPER_SECURE_PASSWORD_IN_PRODUCTION" ]; then
        print_error "DB_PASSWORD must be changed in production!"
        exit 1
    fi
    
    # Build and deploy
    print_status "Building production image..."
    docker build -t fastapi-users-api:latest .
    
    print_success "Production deployment ready!"
    echo "To run: docker run -d --env-file .env -p 8000:8000 fastapi-users-api:latest"
}

# Function to deploy to AWS
deploy_aws() {
    print_status "Deploying to AWS..."
    print_warning "This is a basic AWS deployment guide. Customize for your specific setup."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        exit 1
    fi
    
    print_status "AWS deployment steps:"
    echo "1. Create an EC2 instance"
    echo "2. Install Docker on the instance"
    echo "3. Copy your application files to the instance"
    echo "4. Configure .env.production with your database settings"
    echo "5. Run: docker build -t fastapi-users-api ."
    echo "6. Run: docker run -d --env-file .env -p 80:8000 fastapi-users-api"
    
    print_warning "For production AWS deployment, consider using:"
    echo "- AWS ECS or EKS for container orchestration"
    echo "- AWS RDS for managed PostgreSQL"
    echo "- AWS ALB for load balancing"
    echo "- AWS Route 53 for DNS"
    echo "- AWS Certificate Manager for SSL"
}

# Main deployment logic
main() {
    echo "==============================================================================="
    echo "FastAPI Users Project - Deployment Script"
    echo "==============================================================================="
    
    ENVIRONMENT=${1:-local}
    
    case $ENVIRONMENT in
        local)
            check_requirements
            deploy_local
            ;;
        docker)
            deploy_docker
            ;;
        production)
            deploy_production
            ;;
        aws)
            deploy_aws
            ;;
        *)
            print_error "Unknown environment: $ENVIRONMENT"
            echo "Usage: $0 [local|docker|production|aws]"
            exit 1
            ;;
    esac
    
    print_success "Deployment script completed for environment: $ENVIRONMENT"
}

# Run main function
main "$@"
