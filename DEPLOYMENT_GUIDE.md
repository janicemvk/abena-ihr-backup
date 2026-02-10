# ABENA Healthcare System - Ubuntu Server Deployment Guide

## 🚀 Complete Deployment Guide for Ubuntu Server

This guide will help you deploy the entire ABENA healthcare system on an Ubuntu server using Docker.

## 📋 Server Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or later
- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: 4 cores minimum (8 cores recommended)
- **Storage**: 50GB free space minimum (100GB recommended)
- **Network**: Stable internet connection

### Recommended Specifications
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 16GB or more
- **CPU**: 8 cores or more
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps connection

## 🔧 Step 1: Server Preparation

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Required Packages
```bash
sudo apt install -y curl wget git vim htop unzip
```

### 1.3 Configure Firewall
```bash
# Install UFW if not present
sudo apt install ufw -y

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow ABENA system ports
sudo ufw allow 3001:4012/tcp
sudo ufw allow 5433
sudo ufw allow 6380
sudo ufw allow 8000
sudo ufw allow 8080:8081

# Enable firewall
sudo ufw --force enable
```

## 🐳 Step 2: Docker Installation

### 2.1 Install Docker
```bash
# Remove old Docker versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.2 Configure Docker
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version
```

### 2.3 Configure Docker for Production
```bash
# Create Docker daemon configuration
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "live-restore": true
}
EOF

# Restart Docker
sudo systemctl restart docker
```

## 📦 Step 3: Deploy ABENA System

### 3.1 Upload System Files
```bash
# Create deployment directory
sudo mkdir -p /opt/abena
sudo chown $USER:$USER /opt/abena
cd /opt/abena

# Upload your ABENA system files here
# You can use SCP, SFTP, or Git to transfer files
```

### 3.2 Configure Environment
```bash
# Create production environment file
cat > .env <<EOF
# ABENA Production Environment
NODE_ENV=production
POSTGRES_DB=abena_ihr
POSTGRES_USER=abena_user
POSTGRES_PASSWORD=abena_secure_password_2024
POSTGRES_MULTIPLE_DATABASES=abena_ihr,abena_patients,abena_clinical,abena_blockchain

# JWT Configuration
JWT_SECRET=abena-super-secret-jwt-key-2024-production

# Database URLs
DATABASE_URL=postgresql://abena_user:abena_secure_password_2024@postgres:5432/abena_ihr
REDIS_URL=redis://redis:6379

# Service URLs
AUTH_SERVICE_URL=http://auth-service:3001
SDK_SERVICE_URL=http://sdk-service:3002
MODULE_REGISTRY_URL=http://module-registry:3003
API_GATEWAY_URL=http://api-gateway
EOF
```

### 3.3 Update Docker Compose for Production
```bash
# Create production docker-compose file
cat > docker-compose.prod.yml <<EOF
version: '3.8'

services:
  # Database Services
  postgres:
    image: postgres:15-alpine
    container_name: abena-postgres
    environment:
      POSTGRES_DB: abena_ihr
      POSTGRES_USER: abena_user
      POSTGRES_PASSWORD: abena_secure_password_2024
      POSTGRES_MULTIPLE_DATABASES: abena_ihr,abena_patients,abena_clinical,abena_blockchain
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./ABENA PATIENT DATABASE.sql:/docker-entrypoint-initdb.d/01-patient-db.sql
      - ./IHR Database.sql:/docker-entrypoint-initdb.d/02-ihr-db.sql
      - ./ABENA CLINICAL DATA.sql:/docker-entrypoint-initdb.d/03-clinical-db.sql
      - ./ABENA BLOCKCHAIN STATUS.sql:/docker-entrypoint-initdb.d/04-blockchain-db.sql
      - ./ABENA IHR.sql:/docker-entrypoint-initdb.d/05-abena-ihr.sql
    networks:
      - abena-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U abena_user -d abena_ihr"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: abena-redis
    ports:
      - "6380:6379"
    volumes:
      - redis_data:/data
    networks:
      - abena-network
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Core Services
  auth-service:
    build:
      context: ./auth-service
      dockerfile: Dockerfile
    container_name: abena-auth-service
    environment:
      - NODE_ENV=production
      - PORT=3001
      - JWT_SECRET=abena-super-secret-jwt-key-2024-production
      - DATABASE_URL=postgresql://abena_user:abena_secure_password_2024@postgres:5432/abena_ihr
      - REDIS_URL=redis://redis:6379
    ports:
      - "3001:3001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - abena-network
    restart: unless-stopped

  sdk-service:
    build:
      context: ./abena_unified_integration/Abena Shared SDK -universal Service Client/shared-libraries/abena-sdk
      dockerfile: Dockerfile
    container_name: abena-sdk-service
    environment:
      - NODE_ENV=production
      - PORT=3002
      - AUTH_SERVICE_URL=http://auth-service:3001
    ports:
      - "3002:3002"
    depends_on:
      - auth-service
    networks:
      - abena-network
    restart: unless-stopped

  # Add all other services with restart: unless-stopped
  # ... (include all services from your docker-compose.yml)
EOF
```

## 🚀 Step 4: Start the System

### 4.1 Build and Start Services
```bash
# Build all services
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

### 4.2 Verify Deployment
```bash
# Check all containers are running
docker ps

# Test key endpoints
curl http://localhost:4002/health
curl http://localhost:8000
curl http://localhost:4009
```

## 🔒 Step 5: Security Configuration

### 5.1 SSL/TLS Setup (Optional but Recommended)
```bash
# Install Certbot for SSL certificates
sudo apt install certbot -y

# Get SSL certificate (replace your-domain.com with your actual domain)
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx reverse proxy with SSL
sudo apt install nginx -y
```

### 5.2 Create Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/abena <<EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Main Portal
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Provider Dashboard
    location /provider {
        proxy_pass http://localhost:4009;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Patient Dashboard
    location /patient {
        proxy_pass http://localhost:4010;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # eCDome Intelligence
    location /ecdome {
        proxy_pass http://localhost:4005;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/abena /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Step 6: Monitoring and Maintenance

### 6.1 Create Monitoring Script
```bash
cat > monitor-abena.sh <<EOF
#!/bin/bash
echo "=== ABENA System Status ==="
echo "Date: \$(date)"
echo ""

echo "=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== System Resources ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1

echo "Memory Usage:"
free -h

echo "Disk Usage:"
df -h /

echo ""
echo "=== Service Health Checks ==="
curl -s http://localhost:4002/health | head -1
curl -s http://localhost:8000 | head -1
curl -s http://localhost:4009 | head -1
EOF

chmod +x monitor-abena.sh
```

### 6.2 Create Backup Script
```bash
cat > backup-abena.sh <<EOF
#!/bin/bash
BACKUP_DIR="/opt/abena/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

echo "Creating backup: abena_backup_\$DATE"

# Backup database
docker exec abena-postgres pg_dump -U abena_user abena_ihr > \$BACKUP_DIR/database_\$DATE.sql

# Backup volumes
docker run --rm -v abena_all_postgres_data:/data -v \$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data_\$DATE.tar.gz -C /data .

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: abena_backup_\$DATE"
EOF

chmod +x backup-abena.sh
```

### 6.3 Set up Cron Jobs
```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/abena/backup-abena.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/abena/monitor-abena.sh >> /opt/abena/monitor.log") | crontab -
```

## 🔧 Step 7: Troubleshooting

### 7.1 Common Issues and Solutions

#### Port Conflicts
```bash
# Check what's using ports
sudo netstat -tulpn | grep :4002
sudo lsof -i :4002

# Kill processes if needed
sudo kill -9 <PID>
```

#### Container Issues
```bash
# Check container logs
docker logs abena-ihr-main
docker logs abena-postgres

# Restart specific service
docker compose -f docker-compose.prod.yml restart abena-ihr
```

#### Database Issues
```bash
# Connect to database
docker exec -it abena-postgres psql -U abena_user -d abena_ihr

# Check database status
docker exec abena-postgres pg_isready -U abena_user
```

## 📋 Step 8: Production Checklist

### Before Going Live:
- [ ] All containers are running
- [ ] Database is healthy
- [ ] SSL certificates are installed
- [ ] Firewall is configured
- [ ] Monitoring is set up
- [ ] Backup system is working
- [ ] All services respond to health checks
- [ ] Domain is pointing to server
- [ ] Security updates are applied

### Access URLs:
- **Main Portal**: https://your-domain.com
- **Provider Dashboard**: https://your-domain.com/provider
- **Patient Dashboard**: https://your-domain.com/patient
- **eCDome Intelligence**: https://your-domain.com/ecdome
- **Admin Dashboard**: https://your-domain.com:8080

## 🆘 Support and Maintenance

### Daily Tasks:
- Monitor system health
- Check backup status
- Review logs for errors

### Weekly Tasks:
- Update system packages
- Review security logs
- Test backup restoration

### Monthly Tasks:
- Update Docker images
- Review and rotate logs
- Security audit

---

**Deployment Complete!** 🎉

Your ABENA healthcare system is now running on Ubuntu server with Docker. All services are containerized, monitored, and backed up automatically.
