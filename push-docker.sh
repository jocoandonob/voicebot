#!/bin/bash

# Check if username is provided
if [ -z "$1" ]; then
    echo "Please provide your Docker Hub username"
    echo "Usage: ./push-docker.sh yourusername"
    exit 1
fi

USERNAME=$1
IMAGE_NAME="voice-ai-assistant"
TAG="latest"

# Build the image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Tag the image
echo "Tagging image..."
docker tag $IMAGE_NAME $USERNAME/$IMAGE_NAME:$TAG

# Push the image
echo "Pushing to Docker Hub..."
docker push $USERNAME/$IMAGE_NAME:$TAG

echo "Done! Your image is now available at: docker.io/$USERNAME/$IMAGE_NAME:$TAG" 