# ABENA Healthcare System - Deployment Checklist

## 🚀 Quick Deployment Checklist for Ubuntu Server

### Pre-Deployment Requirements
- [ ] Ubuntu 20.04 LTS or later
- [ ] Minimum 8GB RAM (16GB recommended)
- [ ] Minimum 4 CPU cores (8 cores recommended)
- [ ] 50GB free disk space (100GB recommended)
- [ ] Root/sudo access to server
- [ ] Internet connection for Docker installation

### Step 1: Server Preparation
- [ ] Update system packages (`sudo apt update && sudo apt upgrade -y`)
- [ ] Install required packages (`sudo apt install -y curl wget git vim htop unzip ufw`)
- [ ] Configure firewall (ports 80, 443, 3001-4012, 5433, 6380, 8000, 8080-8081)

### Step 2: Docker Installation
- [ ] Remove old Docker versions
- [ ] Add Docker's official GPG key
- [ ] Set up Docker repository
- [ ] Install Docker CE and Docker Compose
- [ ] Add user to docker group
- [ ] Start and enable Docker service
- [ ] Verify Docker installation (`docker --version`)

### Step 3: ABENA System Deployment
- [ ] Create deployment directory (`/opt/abena`)
- [ ] Upload ABENA system files to server
- [ ] Copy `docker-compose.prod.yml` to deployment directory
- [ ] Create production environment file (`.env`)
- [ ] Build all services (`docker compose -f docker-compose.prod.yml build`)
- [ ] Start all services (`docker compose -f docker-compose.prod.yml up -d`)

### Step 4: Verification
- [ ] Check all containers are running (`docker ps`)
- [ ] Test main portal (http://server-ip:8000)
- [ ] Test provider dashboard (http://server-ip:4009)
- [ ] Test patient dashboard (http://server-ip:4010)
- [ ] Test eCDome intelligence (http://server-ip:4005)
- [ ] Test admin dashboard (http://server-ip:8080)
- [ ] Test API health endpoints

### Step 5: Production Configuration
- [ ] Change default passwords
- [ ] Configure SSL/TLS certificates (optional)
- [ ] Set up domain names
- [ ] Configure monitoring scripts
- [ ] Set up backup scripts
- [ ] Configure systemd service for auto-start

### Step 6: Security Hardening
- [ ] Update all default passwords
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting
- [ ] Configure backup and recovery

## 🎯 Quick Start Commands

### Automated Deployment
```bash
# Run the automated deployment script
./deploy.sh
```

### Manual Deployment
```bash
# 1. Prepare server
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip ufw

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Deploy ABENA
sudo mkdir -p /opt/abena
sudo chown $USER:$USER /opt/abena
cd /opt/abena

# 4. Copy your ABENA files here, then:
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## 📊 Post-Deployment Verification

### Check System Status
```bash
# Check all containers
docker ps

# Check system resources
./monitor-abena.sh

# Check service health
curl http://localhost:4002/health
curl http://localhost:8000
curl http://localhost:4009
```

### Access URLs
- **Main Portal**: http://your-server-ip:8000
- **Provider Dashboard**: http://your-server-ip:4009
- **Patient Dashboard**: http://your-server-ip:4010
- **eCDome Intelligence**: http://your-server-ip:4005
- **Admin Dashboard**: http://your-server-ip:8080
- **API Gateway**: http://your-server-ip:8081

## 🔧 Troubleshooting

### Common Issues
1. **Port conflicts**: Check what's using ports with `sudo netstat -tulpn | grep :PORT`
2. **Container issues**: Check logs with `docker logs container-name`
3. **Database issues**: Connect with `docker exec -it abena-postgres psql -U abena_user -d abena_ihr`
4. **Permission issues**: Ensure user is in docker group with `sudo usermod -aG docker $USER`

### Useful Commands
```bash
# Restart specific service
docker compose -f docker-compose.prod.yml restart service-name

# View logs
docker logs -f container-name

# Check resource usage
docker stats

# Backup database
./backup-abena.sh

# Monitor system
./monitor-abena.sh
```

## 📋 Production Checklist

### Security
- [ ] Change all default passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set up proper firewall rules
- [ ] Enable log monitoring
- [ ] Set up intrusion detection

### Monitoring
- [ ] Set up system monitoring
- [ ] Configure log aggregation
- [ ] Set up alerting
- [ ] Monitor resource usage
- [ ] Track application performance

### Backup & Recovery
- [ ] Set up automated backups
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Set up disaster recovery
- [ ] Regular backup testing

### Maintenance
- [ ] Schedule regular updates
- [ ] Monitor security patches
- [ ] Plan maintenance windows
- [ ] Document procedures
- [ ] Train support staff

---

**Deployment Status**: ✅ Ready for Production
