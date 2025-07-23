# 🚀 FastAPI Users Project - Deployment Guide

## 📋 Overview

This guide explains how to deploy the FastAPI Users Project in different environments by simply changing the `.env` file. The project supports:

- **Local Development** (SQLite)
- **Docker Development** (PostgreSQL in containers)
- **Production Server** (Remote PostgreSQL)
- **AWS Cloud** (EC2 + RDS)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI App   │    │   PostgreSQL    │
│   (Optional)    │◄──►│   (Gunicorn +   │◄──►│   Database      │
│                 │    │    Uvicorn)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## � Prerequisites

### System Requirements:
- **Python 3.9+** (check with `python --version`)
- **Docker & Docker Compose** (for containerized deployments)
- **Git** (for cloning and version control)
- **PostgreSQL** (for production deployments)

### Installation Commands:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv docker.io docker-compose git

# macOS (with Homebrew)
brew install python docker docker-compose git

# Windows
# Download Python from python.org
# Download Docker Desktop from docker.com
```

## �🔧 Environment Files

### Available Environment Files:
- `.env.local` - Local development with SQLite
- `.env.docker` - Docker development with PostgreSQL
- `.env.production` - Production deployment
- `.env.example` - Template for all environments

### Critical Environment Variables:
```bash
# Security (MUST change in production)
SECRET_KEY=your-secret-key-32-chars-minimum
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fastapi_users_db
DB_USER=fastapi_user
DB_PASSWORD=secure_password

# CORS (restrict in production)
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Monitoring
ENABLE_HEALTH_CHECKS=true
ENABLE_SECURITY_HEADERS=true
```

## 🚀 Deployment Methods

### 1. Local Development (SQLite)

**Use Case**: Quick development and testing without Docker

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd fastapi_users_project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Copy local environment
cp .env.local .env

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

**Database**: SQLite file (`dev.db`)
**Pros**: Fast setup, no Docker required
**Cons**: Limited to SQLite features

### 2. Docker Development (PostgreSQL)

**Use Case**: Development with production-like database

```bash
# 1. Clone the repository (if not done)
git clone <your-repo-url>
cd fastapi_users_project

# 2. Copy Docker environment
# Option 1:
cp .env.docker .env

# 3. Start with Docker Compose
docker-compose up --build

# Option 2:
docker-compose --env-file .env.docker up --build

# 4. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
# Database: localhost:5432

# 5. Stop services
docker-compose down
```

**Database**: PostgreSQL in Docker container
**Pros**: Production-like environment, easy setup
**Cons**: Requires Docker

### 3. Production Server Deployment

**Use Case**: Deploy to your own server (LSV-Tech, VPS, etc.)

```bash
# 1. Prepare server (Ubuntu 22.04 LTS recommended)
sudo apt update
sudo apt install docker.io docker-compose git

# 2. Clone project
git clone <your-repo-url>
cd fastapi_users_project

# 3. Configure production environment
cp .env.production .env

# 4. Edit .env with your production settings
nano .env

# 5. Update these critical values:
# - SECRET_KEY (minimum 32 characters)
# - DB_HOST (your database server)
# - DB_PASSWORD (secure password)
# - ALLOWED_ORIGINS (your domain)
# - DEBUG=false

# 6. Generate secure secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# 7. Build and run
docker build -t fastapi-users-api .
docker run -d \
  --name fastapi-users-api \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  fastapi-users-api

# 8. Verify deployment
curl http://your-server:8000/health
```

**Database**: External PostgreSQL server
**Pros**: Full control, production-ready
**Cons**: Requires server management

### 4. AWS Cloud Deployment

**Use Case**: Scalable cloud deployment

#### Step 1: Setup RDS Database
```bash
# 1. Create RDS PostgreSQL instance
# - Engine: PostgreSQL 15+
# - Instance class: db.t3.micro (for testing)
# - Storage: 20GB minimum
# - Public access: Yes (for initial setup)
# - Security group: Allow port 5432 from your EC2

# 2. Note the RDS endpoint for .env configuration
```

#### Step 2: Setup EC2 Instance
```bash
# 1. Launch EC2 instance (Ubuntu 22.04 LTS recommended)
# - Instance type: t3.micro (for testing)
# - Security group: Allow HTTP (80), HTTPS (443), SSH (22)

# 2. Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# 4. Clone your project
git clone <your-repo-url>
cd fastapi_users_project

# 5. Configure for AWS
cp .env.production .env
nano .env  # Update with RDS endpoint and settings

# Example AWS .env configuration:
# DATABASE_URL=postgresql+asyncpg://username:password@your-rds-endpoint:5432/fastapi_users_db
# DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
# ALLOWED_ORIGINS=https://yourdomain.com

# 6. Deploy
docker build -t fastapi-users-api .
docker run -d \
  --name fastapi-users-api \
  --env-file .env \
  -p 80:8000 \
  --restart unless-stopped \
  fastapi-users-api

# 7. Configure security group to allow HTTP/HTTPS traffic
```

## 🔄 Using the Deployment Script

The project includes an automated deployment script:

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy to different environments
./scripts/deploy.sh local     # Local development
./scripts/deploy.sh docker    # Docker development
./scripts/deploy.sh production # Production server
./scripts/deploy.sh aws       # AWS deployment

# The script will:
# 1. Validate environment
# 2. Copy appropriate .env file
# 3. Install/build dependencies
# 4. Start the application
# 5. Run health checks
```

## 🐳 Advanced Docker Commands

### Environment-Based Deployment

```bash
# Development mode (Uvicorn with hot reload)
cp .env.docker .env
echo "ENVIRONMENT=development" >> .env
docker-compose up --build

# Production mode (Gunicorn + Uvicorn workers)
cp .env.production .env
echo "ENVIRONMENT=production" >> .env
docker-compose up --build

# With additional services (Redis + Nginx)
docker-compose --profile production up --build
# or
docker-compose --profile redis up --build  # Just Redis
docker-compose --profile nginx up --build  # Just Nginx
```

### Service Management

```bash
# Start specific services
docker-compose up web db          # Only API and database
docker-compose up web db redis    # API, database, and Redis

# Scale services
docker-compose up --scale web=3   # Run 3 API instances

# View logs
docker-compose logs -f web        # API logs
docker-compose logs -f db         # Database logs
docker-compose logs -f            # All services

# Execute commands in containers
docker-compose exec web bash      # Shell in API container
docker-compose exec db psql -U fastapi_user -d fastapi_users_db
```

## 📁 Project Structure

```
fastapi_users_project/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   ├── security.py           # Authentication & security
│   │   ├── lifespan.py           # Application lifecycle
│   │   ├── logging_config.py     # Logging configuration
│   │   └── middleware.py         # Custom middlewares
│   ├── db/                       # Database related
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy base
│   │   └── database.py           # Database connection
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py               # User model
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user_schema.py        # User schemas
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py       # User service
│   ├── routers/                  # API routes
│   │   ├── __init__.py
│   │   ├── user_router.py        # User endpoints
│   │   └── health_router.py      # Health check endpoints
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── jwt.py                # JWT utilities
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   └── test_users.py             # User tests
├── scripts/                      # Deployment scripts
│   ├── deploy.sh                 # Automated deployment
│   └── init-db.sql               # Database initialization
├── logs/                         # Application logs (created at runtime)
├── nginx/                        # Nginx configuration (optional)
│   ├── nginx.conf
│   └── ssl/
├── .env                          # Current environment (git-ignored)
├── .env.example                  # Environment template
├── .env.local                    # Local development
├── .env.docker                   # Docker development
├── .env.production               # Production deployment
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker services
├── gunicorn_conf.py              # Gunicorn configuration
├── pytest.ini                   # Test configuration
├── README.md                     # Project documentation
├── DEPLOYMENT_GUIDE.md           # This deployment guide
└── LICENSE                       # Project license
```

### Key Files Explained

| **File** | **Purpose** | **Environment** |
|----------|-------------|-----------------|
| `.env.local` | SQLite, development settings | Local development |
| `.env.docker` | PostgreSQL in Docker | Docker development |
| `.env.production` | Production database, security | Production deployment |
| `gunicorn_conf.py` | Production server configuration | Production |
| `docker-compose.yml` | Multi-service orchestration | Docker/Production |
| `scripts/deploy.sh` | Automated deployment | All environments |

## 🔍 Testing Deployments

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check (includes DB, system resources)
curl http://localhost:8000/api/v1/health/detailed

# Kubernetes probes
curl http://localhost:8000/api/v1/health/ready
curl http://localhost:8000/api/v1/health/live
```

### API Testing

```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Get current user (requires token)
TOKEN="your-jwt-token-here"
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

## 🚨 Security Checklist

### Before Production Deployment:

- [ ] **Change `SECRET_KEY`** to a secure 32+ character string
- [ ] **Change all default passwords** (database, admin accounts)
- [ ] **Configure `ALLOWED_ORIGINS`** to your specific domains only
- [ ] **Use HTTPS in production** (SSL certificates)
- [ ] **Set `DEBUG=false`** in production
- [ ] **Configure proper database user permissions** (not superuser)
- [ ] **Enable security headers** (`ENABLE_SECURITY_HEADERS=true`)
- [ ] **Set up proper logging** (file rotation, log levels)
- [ ] **Configure firewall rules** (only necessary ports open)
- [ ] **Set up SSL certificates** (Let's Encrypt recommended)
- [ ] **Enable database backups** (automated daily backups)
- [ ] **Monitor application logs** (centralized logging)
- [ ] **Set up monitoring alerts** (CPU, memory, disk usage)

### AWS-Specific Security:
- [ ] **Configure VPC** with private subnets for RDS
- [ ] **Use IAM roles** instead of access keys
- [ ] **Enable CloudWatch** for monitoring
- [ ] **Set up Application Load Balancer** for HTTPS termination
- [ ] **Configure Auto Scaling** for high availability

## 🔧 Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   ```bash
   # Check database connectivity
   docker-compose logs db
   
   # Verify environment variables
   cat .env | grep DB_
   
   # Test database connection manually
   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
   
   # Check if database service is running
   docker-compose ps
   ```

2. **Permission Denied**
   ```bash
   # Fix file permissions
   chmod +x scripts/deploy.sh
   sudo chown -R $USER:$USER .
   
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   sudo lsof -i :8000
   sudo kill -9 PID
   
   # Or use different port
   uvicorn app.main:app --port 8001
   ```

4. **Docker Issues**
   ```bash
   # Clean Docker system
   docker system prune -a
   docker-compose down --volumes
   
   # Rebuild containers
   docker-compose up --build --force-recreate
   
   # Check Docker daemon
   sudo systemctl status docker
   ```

5. **Import Errors**
   ```bash
   # Ensure you're in the project root
   pwd  # Should show fastapi_users_project
   
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Verify virtual environment
   which python
   ```

6. **JWT Token Issues**
   ```bash
   # Verify SECRET_KEY is set and long enough
   echo $SECRET_KEY | wc -c  # Should be 32+ characters
   
   # Check token expiration
   # Default is 30 minutes, check ACCESS_TOKEN_EXPIRE_MINUTES
   ```

## 📈 Monitoring and Maintenance

### Log Files:
- **Application logs**: `logs/app.log`
- **Error logs**: `logs/error.log`
- **Docker logs**: `docker-compose logs`
- **System logs**: `/var/log/syslog`

### Performance Monitoring:
- **Health checks**: `/api/v1/health/detailed`
- **System metrics**: CPU, memory, disk usage via `/api/v1/health/detailed`
- **Database performance**: Connection pool, query times
- **Response times**: Monitor API endpoint latency

### Backup Strategy:
- **Database backups**: Regular PostgreSQL dumps
  ```bash
  # Create backup
  pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql
  
  # Restore backup
  psql -h $DB_HOST -U $DB_USER $DB_NAME < backup_20240101.sql
  ```
- **Application files**: Git repository with tags
- **Environment files**: Secure storage (without secrets)

### Maintenance Tasks:
- **Weekly**: Check logs for errors
- **Monthly**: Update dependencies (`pip list --outdated`)
- **Quarterly**: Security audit and penetration testing

## 🎯 Quick Reference

### Environment Switch Commands:

```bash
# Switch to local development
cp .env.local .env && uvicorn app.main:app --reload

# Switch to Docker development
cp .env.docker .env && docker-compose up --build

# Switch to production
cp .env.production .env && docker build -t fastapi-users-api .
```

### Useful URLs:
- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Detailed Health**: `http://localhost:8000/api/v1/health/detailed`
- **User Registration**: `POST /api/v1/users/register`
- **User Login**: `POST /api/v1/users/login`

### Docker Commands:
```bash
# View running containers
docker ps

# View logs
docker logs fastapi-users-api

# Execute commands in container
docker exec -it fastapi-users-api bash

# Stop and remove container
docker stop fastapi-users-api && docker rm fastapi-users-api
```

---

## 🆘 Support

If you encounter issues:

1. **Check the logs**: `docker-compose logs` or `logs/app.log`
2. **Verify environment variables**: `cat .env`
3. **Test health endpoint**: `curl http://localhost:8000/health`
4. **Check database connectivity**: `docker-compose exec db psql -U $DB_USER -d $DB_NAME`
5. **Verify Python environment**: `which python` and `pip list`
6. **Check port availability**: `sudo lsof -i :8000`

### Getting Help:
- **Documentation**: Check `/docs` endpoint for API documentation
- **Logs**: Always check application and system logs first
- **Health Checks**: Use detailed health endpoint for system status
- **Testing**: Run the test suite to verify functionality

**Remember**: The key to easy deployment is proper environment configuration. Change only the `.env` file to switch between environments!

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Docker Documentation**: https://docs.docker.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Nginx Configuration**: For reverse proxy setup
- **Let's Encrypt**: For free SSL certificates
