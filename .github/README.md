# GitHub Actions CI/CD Pipeline

This repository includes a comprehensive GitHub Actions workflow that handles testing, building, and deploying your crawler service.

## Workflow Features

- **Automated Testing**: Runs pytest unit tests and integration tests
- **Docker Image Building**: Builds and pushes Docker images to GitHub Container Registry
- **Multi-Environment Deployment**: Supports staging and production deployments
- **Health Checks**: Verifies service health after deployment
- **Manual Deployment**: Allows manual triggering with environment selection

## Test Structure

The workflow runs two types of tests:

1. **Unit Tests** (`test_crawler.py`): Fast pytest tests using FastAPI TestClient
2. **Integration Tests** (`test_service.py`): End-to-end tests against running service

Both test files are included and will be executed during the CI/CD pipeline.

## Setup Instructions

### 1. Docker Registry Setup

⚠️ **Important**: Configure your Docker registry before running the workflow.

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed instructions on:
- GitHub Container Registry (GHCR) setup
- Docker Hub setup (recommended for easier configuration)
- Troubleshooting registry permission issues

### 2. Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

#### For Docker Hub (Recommended)
```
DOCKER_USERNAME            # Your Docker Hub username
DOCKER_PASSWORD            # Your Docker Hub access token
```

#### For GitHub Container Registry (Alternative)
No additional secrets needed - uses GITHUB_TOKEN automatically.

#### For SSH Deployment (Docker Compose)
```
SSH_PRIVATE_KEY          # Your SSH private key for server access
STAGING_HOST            # Staging server hostname/IP
STAGING_USER            # SSH username for staging
PROD_HOST              # Production server hostname/IP  
PROD_USER              # SSH username for production
SSH_PORT               # SSH port (optional, defaults to 22)
```

#### For Service URLs (Health Checks)
```
STAGING_SERVICE_URL     # http://your-staging-domain.com
PROD_SERVICE_URL       # http://your-production-domain.com
```

#### For Kubernetes Deployment (Optional)
```
KUBE_CONFIG            # Base64 encoded kubeconfig file
```

### 3. Repository Variables

Set these in your repository variables (Settings → Secrets and variables → Actions → Variables):

```
DOCKER_IMAGE_NAME          # e.g., 'your-dockerhub-username/crawler-service' or 'ghcr.io/your-username/your-repo'
DEPLOYMENT_METHOD          # Options: 'docker-compose', 'kubernetes'
```

### 4. Environment Configuration

Create environments in your GitHub repository (Settings → Environments):

- **staging**: For staging deployments
- **production**: For production deployments (add protection rules as needed)

### 5. Repository Variables

Set these in your repository variables (Settings → Secrets and variables → Actions → Variables):

```
DEPLOYMENT_METHOD      # Options: 'docker-compose', 'kubernetes'
```

If not set, defaults to 'docker-compose'.

## How It Works

### Automatic Triggers
- **Push to main/master**: Runs tests → builds image → deploys to staging
- **Pull Requests**: Runs tests and builds image (no deployment)
- **Tags (v*)**: Runs full pipeline with semantic versioning

### Manual Deployment
1. Go to Actions tab in your repository
2. Select "Build and Deploy Crawler Service"
3. Click "Run workflow"
4. Choose environment: staging, production, or skip deployment

## Server Setup

### For Docker Compose Deployment

Your server should have:
1. Docker and Docker Compose installed
2. Directory `/opt/crawler-service` created
3. SSH access configured
4. Port 8000 accessible (or configure your reverse proxy)

The workflow will automatically create the `docker-compose.yml` file on your server.

### For Kubernetes Deployment

Ensure your cluster has:
1. A deployment named `crawler-service-staging` or `crawler-service-prod`
2. Proper RBAC permissions for the service account
3. Container registry access configured

## Docker Image

Images are built and pushed to: `ghcr.io/your-username/your-repo:tag`

Available tags:
- `latest`: Latest from main branch
- `main-<sha>`: Specific commit from main
- `v1.0.0`: Semantic version tags
- `pr-123`: Pull request builds

## Monitoring

The workflow includes:
- ✅ Automated testing
- ✅ Docker image testing
- ✅ Post-deployment health checks
- ✅ Deployment status notifications

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify SSH_PRIVATE_KEY secret is correct
   - Check server hostname and user credentials
   - Ensure server allows SSH connections

2. **Docker Login Failed**
   - GitHub Container Registry permissions are automatically handled
   - Verify repository visibility settings

3. **Health Check Failed**
   - Check if service is running: `docker ps`
   - Verify port 8000 is accessible
   - Check service logs: `docker-compose logs`

4. **Permission Denied**
   - Ensure SSH user has Docker permissions
   - Add user to docker group: `sudo usermod -aG docker $USER`

### Manual Deployment Commands

If you need to deploy manually:

```bash
# Login to your server
ssh user@your-server

# Navigate to deployment directory
cd /opt/crawler-service

# Pull and restart
docker-compose pull
docker-compose up -d

# Check status
docker-compose ps
curl http://localhost:8000/health
```

## Customization

To modify the deployment process, edit `.github/workflows/ci-cd.yml`:

- Change deployment targets
- Add notification integrations (Slack, Discord, etc.)
- Modify health check endpoints
- Add additional testing steps
- Configure different Docker registries
