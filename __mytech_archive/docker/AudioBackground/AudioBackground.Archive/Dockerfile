# Use a specific version of the official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y portaudio19-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.AudioBackground.txt .

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.AudioBackground.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 4015 available to the world outside this container
EXPOSE 4015

# Define environment variables
ENV QUART_APP=AudioBackground
ENV QUART_ENV=production

# Run the app with a production server
CMD ["hypercorn", "AudioBackground:app", "--bind", "0.0.0.0:4015"]