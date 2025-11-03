#!/bin/bash
# Quick start script for browser-use sandbox

set -e

echo "=========================================="
echo "Browser-use Sandbox Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t browser-use:latest .

echo ""
echo "✓ Docker image built successfully!"
echo ""

# Offer to start the container
read -p "Do you want to start the container now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting container with docker-compose..."
    docker-compose up -d
    
    echo ""
    echo "✓ Container started!"
    echo ""
    echo "Container details:"
    docker-compose ps
    
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To execute commands:"
    echo "  docker exec -it browser-sandbox bash"
    echo ""
    echo "To stop the container:"
    echo "  docker-compose down"
fi

echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo ""
echo "1. Test with the Python client:"
echo "   python browser_client.py --mode local --url https://example.com"
echo ""
echo "2. Run example scripts:"
echo "   docker exec browser-sandbox python3 /home/sandbox/scripts/examples.py"
echo ""
echo "3. Interactive shell:"
echo "   docker exec -it -u sandbox browser-sandbox bash"
echo ""
echo "For more information, see README.md"
echo ""
