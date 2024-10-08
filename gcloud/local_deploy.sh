#!/bin/bash

# Define variables
IMAGE_NAME="gcloud"
CONTAINER_NAME="gcloud"

# Check if COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL is set
if [ -z "$COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL" ]; then
    echo "Error: The environment variable COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL is not set."
    echo "Please set it using: export COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL='your_value'"
    exit 1
else
    echo "COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL is set."
fi

# Build the Docker image
echo "Building the Docker image..."
docker build --build-arg COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL="$COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL" -t $IMAGE_NAME .
# Check if the build succeeded
if [ $? -ne 0 ]; then
    echo "Error: Docker image build failed!"
    exit 1
fi

# Check if a container with the same name is already running and stop it
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping the existing container..."
    docker stop $CONTAINER_NAME
fi

# Check if a container with the same name exists (even if not running) and remove it
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing the existing container..."
    docker rm $CONTAINER_NAME
fi

# Run the container
echo "Running the Docker container..."
docker run -d --name $CONTAINER_NAME -e COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL="$COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL" -p 8080:8080 $IMAGE_NAME

# Check if the container started successfully
if [ $? -eq 0 ]; then
    echo "Container '$CONTAINER_NAME' is running."
else
    echo "Error: Failed to start the container!"
fi
