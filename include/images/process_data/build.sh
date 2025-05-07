IMAGE_NAME="process_data"
TAG="latest"

echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG ./include/images/process_data/

echo "Docker image created successfully!"