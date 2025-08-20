#!/bin/bash

# Docker Run Script for Video Dubbing Tool with Lip Sync
# Convenient script to run the containerized application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="video-dubbing-lipsync"
IMAGE_TAG="${1:-latest}"
CONTAINER_NAME="video-dubbing-app"
HOST_PORT="${2:-5001}"

echo -e "${BLUE}🐳 Running Video Dubbing Tool with Lip Sync${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Image: ${GREEN}${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "Port: ${GREEN}${HOST_PORT}${NC}"
echo -e "Container: ${GREEN}${CONTAINER_NAME}${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if image exists
if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Image ${IMAGE_NAME}:${IMAGE_TAG} not found.${NC}"
    echo -e "${YELLOW}Building the image first...${NC}"
    ./docker-build.sh "${IMAGE_TAG}"
fi

# Stop and remove existing container if running
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
fi

# Create necessary host directories
echo -e "${YELLOW}📁 Preparing host directories...${NC}"
mkdir -p uploads outputs temp

# Run the container
echo -e "${YELLOW}🚀 Starting container...${NC}"

docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:5001" \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/outputs:/app/outputs" \
    -v "$(pwd)/temp:/app/temp" \
    --restart unless-stopped \
    --health-cmd "python healthcheck.py" \
    --health-interval 30s \
    --health-timeout 10s \
    --health-retries 3 \
    --health-start-period 60s \
    "${IMAGE_NAME}:${IMAGE_TAG}"

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting for application to start...${NC}"
sleep 5

# Check container status
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    echo ""
    echo -e "${GREEN}🌐 Application is running at:${NC}"
    echo -e "  ${BLUE}http://localhost:${HOST_PORT}${NC}"
    echo ""
    echo -e "${GREEN}📊 Container Status:${NC}"
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${GREEN}📝 Useful Commands:${NC}"
    echo -e "  ${YELLOW}View logs:${NC} docker logs -f ${CONTAINER_NAME}"
    echo -e "  ${YELLOW}Stop container:${NC} docker stop ${CONTAINER_NAME}"
    echo -e "  ${YELLOW}Restart container:${NC} docker restart ${CONTAINER_NAME}"
    echo -e "  ${YELLOW}Container shell:${NC} docker exec -it ${CONTAINER_NAME} /bin/bash"
    echo -e "  ${YELLOW}Health check:${NC} docker inspect ${CONTAINER_NAME} | grep Health -A 10"
    echo ""
    
    # Test application
    echo -e "${YELLOW}🧪 Testing application...${NC}"
    sleep 10  # Give more time for app to fully start
    
    if curl -s "http://localhost:${HOST_PORT}/test" > /dev/null; then
        echo -e "${GREEN}✅ Application is responding correctly!${NC}"
        echo -e "${GREEN}🎉 Ready to use! Open http://localhost:${HOST_PORT} in your browser${NC}"
    else
        echo -e "${YELLOW}⚠️  Application might still be starting up...${NC}"
        echo -e "${YELLOW}Check logs with: docker logs -f ${CONTAINER_NAME}${NC}"
    fi
    
else
    echo -e "${RED}❌ Container failed to start!${NC}"
    echo -e "${RED}Check logs with: docker logs ${CONTAINER_NAME}${NC}"
    exit 1
fi