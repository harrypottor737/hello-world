#!/bin/bash

# Docker Build Script for Video Dubbing Tool with Lip Sync
# Enhanced build process with optimization and caching

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
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}🐳 Building Docker Image for Video Dubbing Tool with Lip Sync${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "Image: ${GREEN}${FULL_IMAGE_NAME}${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p uploads outputs temp docker/ssl

# Create .gitkeep files for empty directories
touch uploads/.gitkeep outputs/.gitkeep temp/.gitkeep

# Build the Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
echo -e "This may take several minutes for the first build..."
echo ""

# Build with BuildKit for better performance
export DOCKER_BUILDKIT=1

docker build \
    --target production \
    --tag "${FULL_IMAGE_NAME}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo -e "Image: ${GREEN}${FULL_IMAGE_NAME}${NC}"
    
    # Show image details
    echo ""
    echo -e "${BLUE}📊 Image Details:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
    
    echo ""
    echo -e "${GREEN}🚀 Ready to run! Use one of these commands:${NC}"
    echo -e "  ${YELLOW}Simple run:${NC}"
    echo -e "    docker run -p 5001:5001 ${FULL_IMAGE_NAME}"
    echo ""
    echo -e "  ${YELLOW}With volume mounts:${NC}"
    echo -e "    docker run -p 5001:5001 -v \$(pwd)/uploads:/app/uploads -v \$(pwd)/outputs:/app/outputs ${FULL_IMAGE_NAME}"
    echo ""
    echo -e "  ${YELLOW}Using docker-compose:${NC}"
    echo -e "    docker-compose up -d"
    echo ""
    
else
    echo -e "${RED}❌ Docker image build failed!${NC}"
    exit 1
fi