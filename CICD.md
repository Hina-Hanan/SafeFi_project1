# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the SafeFi DeFi Risk Assessment project.

## Overview

The project uses GitHub Actions for automated testing, building, and deployment. The pipeline consists of:

- **CI Pipeline**: Automated testing, linting, and Docker image building
- **CD Pipeline**: Automated deployment to production environments
- **Containerization**: Docker multi-stage builds for optimized production images

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Repository                    │
└─────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐   ┌──────────────┐
            │  CI Pipeline │   │  CD Pipeline │
            └──────────────┘   └──────────────┘
                    │                   │
                    ▼                   ▼
            ┌──────────────┐   ┌──────────────┐
            │   Build &    │   │ Deploy to    │
            │    Test      │   │ Production   │
            └──────────────┘   └──────────────┘
```

## CI Pipeline

The CI pipeline (`ci.yml`) runs on every push to `main` or `develop` branches and on pull requests.

### Jobs

1. **Backend Lint and Test**
   - Python environment setup
   - Linting with flake8
   - Format checking with black
   - Type checking with mypy
   - Running tests with pytest and coverage

2. **Frontend Lint and Test**
   - Node.js environment setup
   - Linting with ESLint
   - TypeScript type checking
   - Building the frontend application

3. **Docker Build**
   - Building Docker images for backend and frontend
   - Using Docker Buildx with cache

4. **Security Scan**
   - Vulnerability scanning with Trivy
   - Scanning for critical and high severity issues

### Example Output

```bash
✓ Backend tests passed (coverage: 85%)
✓ Frontend built successfully
✓ Docker images built
✓ Security scan completed (0 vulnerabilities found)
```

## CD Pipeline

The CD pipeline (`deploy.yml`) runs on pushes to `main` branch or when a tag is pushed.

### Jobs

1. **Build and Push Docker Images**
   - Builds Docker images for backend and frontend
   - Pushes images to GitHub Container Registry (ghcr.io)
   - Tags images with SHA, branch, and version tags

2. **Deploy to Production**
   - SSH deployment to production server
   - Pulls latest code and Docker images
   - Updates containers with zero-downtime strategy
   - Runs database migrations
   - Performs health checks

3. **Post-Deployment Tests**
   - Tests API health endpoint
   - Tests frontend availability
   - Validates API response structure

### Deployment Process

```bash
1. SSH to production server
2. Navigate to project directory
3. Pull latest Git changes
4. Login to GitHub Container Registry
5. Pull latest Docker images
6. Stop existing containers gracefully
7. Start new containers
8. Run database migrations
9. Verify health endpoints
```

## Docker Configuration

### Multi-Stage Builds

Both backend and frontend use multi-stage Docker builds for optimal image sizes:

#### Backend Dockerfile

```dockerfile
# Builder stage
FROM python:3.11-slim AS builder
# Install dependencies

# Production stage
FROM python:3.11-slim
# Copy only necessary files
# Run as non-root user
```

**Features:**
- Multi-stage build for smaller images
- Non-root user for security
- Health check endpoint
- Production-optimized uvicorn workers

#### Frontend Dockerfile

```dockerfile
# Builder stage
FROM node:20-alpine AS builder
# Build application

# Production stage
FROM nginx:alpine
# Serve static files
```

**Features:**
- Multi-stage build
- Custom nginx configuration
- Security headers
- Gzip compression
- Client-side routing support

## Docker Compose

The project uses Docker Compose for orchestrating services:

### Services

- **db**: PostgreSQL database
- **mlflow**: MLflow model tracking
- **api**: FastAPI backend
- **frontend**: React frontend with nginx

### Configuration

Services are configured with:
- Health checks
- Restart policies
- Network isolation
- Volume management
- Environment variables

## Deployment

### Prerequisites

1. Server with Docker and Docker Compose installed
2. SSH access to the server
3. GitHub secrets configured:
   - `PROD_HOST`: Production server hostname
   - `PROD_USER`: SSH username
   - `PROD_SSH_KEY`: SSH private key
   - `PROD_PORT`: SSH port (optional)

### Manual Deployment

```bash
# 1. Setup production environment
cd deploy
./setup-production.sh

# 2. Update environment variables
nano .env.production

# 3. Deploy
./deploy.sh

# 4. Check health
./health-check.sh
```

### Environment Variables

Key environment variables for production:

```bash
# Database
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=defi_risk_assessment

# API
API_PORT=8000
CORS_ORIGINS=https://safefi.app

# Email
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
ALERT_SENDER_EMAIL=<email>
ALERT_SENDER_PASSWORD=<password>
```

## Monitoring

### Health Checks

All services include health check endpoints:

- Frontend: `GET /health`
- Backend: `GET /health`
- Database: PostgreSQL readiness check
- MLflow: `GET /health`

### Logs

View service logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

### Monitoring Tools

- **Health Checks**: Docker Compose health checks
- **Application Metrics**: Available via `/metrics` endpoint
- **Error Tracking**: Structured JSON logs

## Security

### Security Features

1. **Non-root Containers**: All containers run as non-root users
2. **Security Scanning**: Trivy scans for vulnerabilities
3. **Secure Headers**: Security headers in nginx configuration
4. **Environment Secrets**: Sensitive data stored as environment variables
5. **Network Isolation**: Services isolated in Docker network

### Best Practices

- Use HTTPS in production
- Rotate secrets regularly
- Monitor security advisories
- Keep dependencies updated
- Use least privilege principles

## Troubleshooting

### CI/CD Issues

**Problem**: Tests failing in CI

```bash
# Run tests locally
cd backend
pytest tests/ -v

# Fix linting issues
black app tests
flake8 app tests
```

**Problem**: Docker build failing

```bash
# Build locally
docker build -t safefi-backend ./backend
docker build -t safefi-frontend ./frontend

# Check logs
docker-compose logs
```

**Problem**: Deployment failing

```bash
# Check SSH connection
ssh user@production-server

# Verify Docker is running
docker ps

# Check service logs
docker-compose logs -f
```

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in .env.production
   API_PORT=8001
   ```

2. **Database Connection Failed**
   ```bash
   # Check database is running
   docker ps | grep postgres
   ```

3. **Out of Memory**
   ```bash
   # Reduce worker count in Dockerfile
   --workers 2
   ```

## Performance Optimization

### Docker Images

- Use multi-stage builds
- Minimize layers
- Use .dockerignore
- Leverage Docker cache

### Application Performance

- Enable gzip compression
- Use CDN for static assets
- Implement caching strategies
- Optimize database queries

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)
