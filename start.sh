#!/bin/bash

if [ -f ".env.staging" ]; then
    ENVIRONMENT="STAGING"
    imageName=backend-staging
    containerName=backend-staging
    portMapping="8080:7443"  # define port mapping for staging
    dockerfilePath=./staging.Dockerfile
elif [ -f ".env.production" ]; then
    ENVIRONMENT="PRODUCTION"
    imageName=backend-production
    containerName=backend-production
    portMapping="8000:7000"  # define port mapping for production
    dockerfilePath=./Dockerfile
else
    echo "Error: No environment file found (.env.staging or .env.production)."
    exit 1
fi

echo "Delete old container..."
sudo docker rm -f $containerName
echo "Delete old image..."
sudo docker rmi $imageName

DOCKER_BUILDKIT=1
sudo docker build -t $imageName . -f $dockerfilePath

echo "Running container for $ENVIRONMENT environment on port $portMapping..."
sudo docker run -e ENVIRONMENT=$ENVIRONMENT -d -p $portMapping --name $containerName $imageName
