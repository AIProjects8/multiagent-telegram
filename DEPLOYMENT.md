# Deployment Guide

This guide covers best practices for deploying the Multiagent Telegram Bot to a VPS server.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (if deploying from repository)
- At least 2GB RAM and 10GB disk space

## Initial Server Setup

### 1. Install Docker and Docker Compose

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in for group changes to take effect.

### 2. Verify Installation

```bash
docker --version
docker compose version
```

## Deployment Methods

### Method 1: Using the Deployment Script (Recommended)

1. **Clone or upload your code to the server:**

```bash
git clone <your-repo-url> /opt/multiagent-telegram
cd /opt/multiagent-telegram
```

2. **Create `.env` file:**

```bash
cp .env.example .env
nano .env
```

Fill in all required environment variables (see `.env.example` for reference).

3. **Make deployment script executable:**

```bash
chmod +x deploy.sh
```

4. **Run deployment:**

```bash
./deploy.sh
```

The script will:
- Check Docker installation
- Stop existing containers
- Pull latest code (if using git)
- Build Docker images
- Start all services
- Show service status and logs

### Method 2: Manual Deployment

1. **Create `.env` file** (same as Method 1)

2. **Build and start services:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. **Check status:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

4. **View logs:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

## Common Issues and Solutions

### Issue 1: Build Fails on VPS but Works Locally

**Possible causes:**
- Architecture mismatch (ARM vs x86)
- Missing system dependencies
- Different Docker versions

**Solutions:**
1. **Check architecture:**
```bash
uname -m
docker version
```

2. **Use platform-specific builds:**
```bash
docker compose build --platform linux/amd64
```

3. **Clear Docker cache:**
```bash
docker system prune -a
docker compose build --no-cache
```

### Issue 2: Permission Denied Errors

**Solution:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Issue 3: Out of Memory During Build

**Solution:**
- Increase swap space
- Build one service at a time
- Use `--memory` limit during build

### Issue 4: Database Connection Errors

**Check:**
1. `.env` file has correct `POSTGRES_HOST=postgres` (not `localhost`)
2. Services are starting in correct order (postgres first)
3. Network connectivity between containers

**Debug:**
```bash
docker compose logs postgres
docker compose exec bot ping postgres
```

### Issue 5: Services Keep Restarting

**Check logs:**
```bash
docker compose logs bot
docker compose logs scheduler
```

Common causes:
- Missing environment variables
- Database not ready
- Application errors

## Updating the Application

### Quick Update (Using Script)

```bash
./deploy.sh
```

### Manual Update

```bash
git pull  # if using git
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring and Maintenance

### View Logs

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f [service_name]
```

### Check Service Health

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker stats
```

### Restart a Service

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart [service_name]
```

### Stop All Services

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Stop and Remove Volumes (⚠️ Deletes Data)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v
```

## Backup and Restore

### Backup Database

```bash
docker compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
docker compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup_file.sql
```

## Security Best Practices

1. **Use strong passwords** in `.env` file
2. **Restrict file permissions:**
```bash
chmod 600 .env
```
3. **Keep Docker updated:**
```bash
sudo apt-get update && sudo apt-get upgrade docker.io
```
4. **Use firewall:**
```bash
sudo ufw allow 22/tcp
sudo ufw enable
```
5. **Regular backups** of database and `.env` file

## Production Recommendations

1. **Use a reverse proxy** (nginx/traefik) if exposing services
2. **Set up log rotation** (already configured in `docker-compose.prod.yml`)
3. **Monitor resource usage** with tools like `htop` or `docker stats`
4. **Set up automated backups** using cron
5. **Use Docker secrets** for sensitive data in production
6. **Enable Docker logging driver** for centralized logging
7. **Use health checks** (already configured)

## Troubleshooting Commands

```bash
docker compose ps                    # List all containers
docker compose logs [service]        # View logs
docker compose exec [service] sh     # Access container shell
docker system df                     # Check disk usage
docker system prune                  # Clean up unused resources
docker images                        # List images
docker ps -a                         # List all containers (including stopped)
```

## Getting Help

If you encounter issues:
1. Check logs: `docker compose logs`
2. Verify `.env` file configuration
3. Ensure all services are healthy: `docker compose ps`
4. Check Docker daemon: `sudo systemctl status docker`

