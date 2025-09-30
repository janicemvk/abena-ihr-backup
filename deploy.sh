#!/bin/bash

# ABENA Healthcare System - Automated Deployment Script
# For Ubuntu Server Deployment

set -e  # Exit on any error

echo "🚀 ABENA Healthcare System - Automated Deployment"
echo "=================================================="

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed. Please install sudo first."
    exit 1
fi

print_status "Starting ABENA system deployment..."

# Step 1: Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install required packages
print_status "Installing required packages..."
sudo apt install -y curl wget git vim htop unzip ufw

# Step 3: Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3001:4012/tcp
sudo ufw allow 5433
sudo ufw allow 6380
sudo ufw allow 8000
sudo ufw allow 8080:8081
sudo ufw --force enable
print_success "Firewall configured"

# Step 4: Install Docker
print_status "Installing Docker..."
if command -v docker &> /dev/null; then
    print_warning "Docker is already installed. Skipping Docker installation."
else
    # Remove old Docker versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
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
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    print_success "Docker installed successfully"
fi

# Step 5: Configure Docker for production
print_status "Configuring Docker for production..."
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

sudo systemctl restart docker
print_success "Docker configured for production"

# Step 6: Create deployment directory
print_status "Setting up deployment directory..."
sudo mkdir -p /opt/abena
sudo chown $USER:$USER /opt/abena
cd /opt/abena

# Step 7: Create production environment file
print_status "Creating production environment configuration..."
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

print_success "Environment configuration created"

# Step 8: Create monitoring script
print_status "Creating monitoring script..."
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
print_success "Monitoring script created"

# Step 9: Create backup script
print_status "Creating backup script..."
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
print_success "Backup script created"

# Step 10: Create systemd service for ABENA
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/abena.service > /dev/null <<EOF
[Unit]
Description=ABENA Healthcare System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/abena
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable abena.service
print_success "Systemd service created and enabled"

print_success "🎉 ABENA deployment preparation completed!"
echo ""
echo "Next steps:"
echo "1. Copy your ABENA system files to /opt/abena/"
echo "2. Update docker-compose.yml for production (add restart: unless-stopped to all services)"
echo "3. Run: docker compose -f docker-compose.prod.yml build"
echo "4. Run: docker compose -f docker-compose.prod.yml up -d"
echo "5. Or use: sudo systemctl start abena"
echo ""
echo "Access URLs (after deployment):"
echo "- Main Portal: http://your-server-ip:8000"
echo "- Provider Dashboard: http://your-server-ip:4009"
echo "- Patient Dashboard: http://your-server-ip:4010"
echo "- eCDome Intelligence: http://your-server-ip:4005"
echo "- Admin Dashboard: http://your-server-ip:8080"
echo ""
echo "Monitoring:"
echo "- Run: ./monitor-abena.sh"
echo "- Check logs: docker logs <container-name>"
echo ""
print_warning "Remember to:"
echo "1. Change default passwords in production"
echo "2. Configure SSL/TLS certificates"
echo "3. Set up proper domain names"
echo "4. Configure firewall rules for your specific needs"
