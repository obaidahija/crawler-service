# Docker Registry Setup Guide

The GitHub Actions workflow supports both GitHub Container Registry (GHCR) and Docker Hub. Here's how to configure each:

## Option 1: GitHub Container Registry (GHCR) - Recommended

### Step 1: Enable GitHub Container Registry

1. Go to your GitHub repository
2. Navigate to **Settings** → **Actions** → **General**
3. Scroll down to **Workflow permissions**
4. Select **"Read and write permissions"**
5. Check **"Allow GitHub Actions to create and approve pull requests"**
6. Click **Save**

### Step 2: Update Repository Variables

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on **Variables** tab
3. Add these repository variables:

```
DOCKER_IMAGE_NAME: ${{ github.repository }}
```

### Step 3: Update Workflow Configuration

In `.github/workflows/ci-cd.yml`, update the env section:

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

### Step 4: Package Visibility Settings

After the first successful build:

1. Go to your GitHub profile/organization
2. Click on **Packages** tab
3. Find your `crawler-service` package
4. Click on it and go to **Package settings**
5. Under **Danger Zone**, change visibility to **Public** (if desired)
6. Under **Manage Actions access**, ensure your repository has **Write** access

## Option 2: Docker Hub - Alternative

### Step 1: Create Docker Hub Account

1. Sign up at [hub.docker.com](https://hub.docker.com)
2. Create a repository named `crawler-service`

### Step 2: Generate Access Token

1. Go to **Account Settings** → **Security**
2. Click **New Access Token**
3. Name it `github-actions`
4. Copy the generated token

### Step 3: Add Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

```
DOCKER_USERNAME: your-dockerhub-username
DOCKER_PASSWORD: your-dockerhub-access-token
```

### Step 4: Add Repository Variables

1. In the **Variables** tab, add:

```
DOCKER_IMAGE_NAME: your-dockerhub-username/crawler-service
```

### Step 5: Update Workflow Configuration

The workflow is already configured to use Docker Hub by default. Just ensure your variables are set correctly.

## Option 3: Fix GHCR Permissions (If you prefer GHCR)

If you're getting "installation not allowed to Create organization package" error:

### For Personal Repositories:

1. Go to GitHub → **Settings** (your profile settings)
2. Click **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
3. Generate a new token with these permissions:
   - Repository: **Contents** (Read), **Metadata** (Read), **Packages** (Write)
4. Add this token as `GITHUB_TOKEN` secret in your repository

### For Organization Repositories:

1. Go to your organization → **Settings**
2. Click **Member privileges**
3. Under **Package creation**, select **"Allow creation of packages"**
4. Under **Package visibility**, configure as needed
5. Go to **Actions** → **General**
6. Under **Fork pull request workflows**, ensure permissions are set correctly

## Current Workflow Configuration

The workflow is currently set to use **Docker Hub** by default because it's more reliable for public repositories. The configuration automatically:

- Uses Docker Hub if `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets exist
- Falls back to GHCR if Docker Hub secrets are not configured
- Supports custom image names via the `DOCKER_IMAGE_NAME` variable

## Testing Your Setup

1. **Push to main branch** or **manually trigger** the workflow
2. Check the **Actions** tab for build progress
3. Verify the image appears in your chosen registry:
   - Docker Hub: `https://hub.docker.com/r/your-username/crawler-service`
   - GHCR: `https://github.com/your-username/your-repo/pkgs/container/crawler-service`

## Troubleshooting

### Common Issues:

1. **Permission denied**: Check workflow permissions and secrets
2. **Package creation failed**: Verify registry settings and access tokens
3. **Authentication failed**: Ensure username/password or tokens are correct

### Debug Steps:

1. Check the Actions logs for specific error messages
2. Verify your registry credentials locally:
   ```bash
   # For Docker Hub
   docker login docker.io
   
   # For GHCR
   echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin
   ```
3. Test pushing manually:
   ```bash
   docker tag your-image registry/username/crawler-service:test
   docker push registry/username/crawler-service:test
   ```

Choose the option that works best for your setup. Docker Hub is generally easier to configure for public repositories, while GHCR integrates better with GitHub's ecosystem.
