#!/bin/bash
set -e

# 1. Create a user-defined Docker network so containers can resolve each other by name
docker network create superkart-net 2>/dev/null || echo "Network superkart-net already exists"

# 2. Build the images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# 3. Remove old containers if they exist
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# 4. Start the Flask backend
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend

# 5. Start the Streamlit frontend, pointing at the backend container
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend  -> port 7860 | Frontend -> port 8501 (see the Ports tab)"
