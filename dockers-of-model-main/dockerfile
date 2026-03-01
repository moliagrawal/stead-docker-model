# FROM python:3.9-slim
# WORKDIR /app
# # Install system packages required by OpenCV, PyTorchVideo, and torchvision
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     libsm6 \
#     libxext6 \
#     libgl1 \
#     git \
#     && rm -rf /var/lib/apt/lists/*
# # Copy everything into the image
# COPY . .
# # Increase timeout in case of slow downloads
# ENV PIP_DEFAULT_TIMEOUT=100
# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
# # Run the model
# CMD ["python", "inference.py"]


# This is the new dockerfile for the above development
# Use a slim, official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system packages required for computer vision
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Increase timeout and install Python dependencies
ENV PIP_DEFAULT_TIMEOUT=100
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user to run the application
RUN useradd --create-home appuser
USER appuser

# Command to run the application
CMD ["python", "inference.py"]
