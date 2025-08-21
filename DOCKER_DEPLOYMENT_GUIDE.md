# 🐳 Docker Deployment Guide - Video Dubbing Tool with Lip Sync

## 🚀 Quick Start

### Method 1: Using Helper Scripts (Recommended)

```bash
# Build the Docker image
./docker-build.sh

# Run the container
./docker-run.sh

# Access the application
open http://localhost:5001
```

### Method 2: Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Method 3: Manual Docker Commands

```bash
# Build the image
docker build -t video-dubbing-lipsync .

# Run the container
docker run -d \
  --name video-dubbing-app \
  -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  video-dubbing-lipsync

# Check status
docker ps
```

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (for compose method)
- At least 4GB RAM available for Docker
- 10GB free disk space (for models and processing)

## 🏗️ Docker Architecture

### Multi-Stage Build Process

1. **Base Stage**: System dependencies (FFmpeg, audio libraries)
2. **Python Dependencies**: Virtual environment with all packages
3. **Model Downloader**: Pre-downloads Whisper models (optional)
4. **Production**: Minimal runtime image with non-root user

### Container Features

- ✅ **Security**: Non-root user execution
- ✅ **Health Checks**: Automatic health monitoring
- ✅ **Volume Mounts**: Persistent data storage
- ✅ **Resource Limits**: Memory and CPU constraints
- ✅ **Auto Restart**: Container restart policies

## 📁 Volume Mapping

| Host Directory | Container Directory | Purpose |
|---------------|-------------------|---------|
| `./uploads/` | `/app/uploads/` | Video file uploads |
| `./outputs/` | `/app/outputs/` | Processed videos |
| `./temp/` | `/app/temp/` | Temporary processing files |

## 🔧 Configuration Options

### Environment Variables

```bash
# Basic configuration
FLASK_APP=app_lipsync.py
FLASK_ENV=production
PYTHONUNBUFFERED=1

# Custom settings (optional)
UPLOAD_MAX_SIZE=500M
PROCESSING_TIMEOUT=600
WHISPER_MODEL=base
```

### Port Configuration

```bash
# Default port mapping
-p 5001:5001

# Custom port mapping
-p 8080:5001  # Access via http://localhost:8080
```

### Resource Limits

```bash
# Memory and CPU limits
docker run \
  --memory=4g \
  --cpus=2.0 \
  -p 5001:5001 \
  video-dubbing-lipsync
```

## 🎛️ Deployment Scenarios

### Development Deployment

```bash
# Simple development setup
docker-compose up -d
```

**Features:**
- Single container
- Local volume mounts
- Development-friendly logging
- Hot reload capabilities

### Production Deployment

```bash
# Production setup with nginx
docker-compose -f docker-compose.prod.yml up -d
```

**Features:**
- Nginx reverse proxy
- SSL/TLS termination
- Redis caching
- Resource limits
- Health monitoring
- Log aggregation

### High Availability Deployment

```bash
# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale video-dubbing-app=3
```

**Features:**
- Multiple app instances
- Load balancing
- Automatic failover
- Monitoring with Prometheus/Grafana

## 🔍 Monitoring & Debugging

### Health Checks

```bash
# Check container health
docker inspect video-dubbing-app | grep Health -A 10

# Manual health check
curl http://localhost:5001/test
```

### Logs

```bash
# View application logs
docker logs -f video-dubbing-app

# View all compose logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f video-dubbing-app
```

### Container Shell Access

```bash
# Access container shell
docker exec -it video-dubbing-app /bin/bash

# Check application status inside container
docker exec video-dubbing-app python healthcheck.py
```

### Performance Monitoring

```bash
# Container resource usage
docker stats video-dubbing-app

# System resource usage
docker system df
docker system events
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs for errors
docker logs video-dubbing-app

# Common causes:
# - Insufficient memory (need 4GB+)
# - Port already in use
# - Permission issues with volumes
```

#### 2. Application Not Responding

```bash
# Check health status
docker inspect video-dubbing-app | grep Health

# Restart container
docker restart video-dubbing-app

# Check if port is accessible
netstat -tulpn | grep 5001
```

#### 3. Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old containers and images
docker container prune
docker image prune -a
```

#### 4. Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limit
docker run --memory=8g -p 5001:5001 video-dubbing-lipsync
```

### Performance Optimization

#### 1. Pre-download Models

```bash
# Use optimized Dockerfile with pre-downloaded models
docker build -f Dockerfile.optimized -t video-dubbing-lipsync:optimized .
```

#### 2. Use SSD Storage

```bash
# Mount volumes on SSD for better performance
docker run \
  -v /path/to/ssd/uploads:/app/uploads \
  -v /path/to/ssd/outputs:/app/outputs \
  -p 5001:5001 \
  video-dubbing-lipsync
```

#### 3. Increase Resources

```bash
# Allocate more resources for faster processing
docker run \
  --memory=8g \
  --cpus=4.0 \
  -p 5001:5001 \
  video-dubbing-lipsync
```

## 🔐 Security Considerations

### Container Security

- ✅ **Non-root user**: Application runs as `appuser`
- ✅ **Read-only filesystem**: Except for data directories
- ✅ **Resource limits**: Prevents resource exhaustion
- ✅ **Health checks**: Automatic failure detection

### Network Security

```bash
# Run with custom network
docker network create video-dubbing-net
docker run --network video-dubbing-net -p 5001:5001 video-dubbing-lipsync
```

### Data Security

```bash
# Secure volume permissions
chmod 755 uploads outputs temp
chown $(id -u):$(id -g) uploads outputs temp
```

## 📊 Production Deployment Checklist

- [ ] **Resources**: Minimum 4GB RAM, 2 CPU cores
- [ ] **Storage**: 20GB+ free disk space
- [ ] **Network**: Firewall rules for port 5001
- [ ] **Monitoring**: Health checks enabled
- [ ] **Backups**: Regular backup of outputs directory
- [ ] **SSL**: HTTPS configuration (production)
- [ ] **Logging**: Centralized log collection
- [ ] **Updates**: Regular security updates

## 🚀 Scaling Options

### Horizontal Scaling

```bash
# Docker Swarm
docker swarm init
docker service create \
  --name video-dubbing \
  --replicas 3 \
  --publish 5001:5001 \
  video-dubbing-lipsync

# Kubernetes
kubectl apply -f k8s-deployment.yaml
```

### Vertical Scaling

```bash
# Increase container resources
docker run \
  --memory=16g \
  --cpus=8.0 \
  -p 5001:5001 \
  video-dubbing-lipsync
```

## 🎯 Best Practices

1. **Use specific image tags** instead of `latest`
2. **Set resource limits** to prevent system overload
3. **Enable health checks** for automatic recovery
4. **Use volume mounts** for persistent data
5. **Monitor logs** regularly for issues
6. **Keep images updated** for security patches
7. **Use multi-stage builds** for smaller images
8. **Implement proper backup** strategies

## 📞 Support

For issues with Docker deployment:

1. Check the logs: `docker logs video-dubbing-app`
2. Verify system requirements
3. Review this guide for troubleshooting steps
4. Check Docker and system resources

The containerized video dubbing tool provides a robust, scalable solution for AI-powered video dubbing with professional lip synchronization!