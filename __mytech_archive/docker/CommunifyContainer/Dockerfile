# Use a specific version of the official Python runtime as a parent image
FROM python:3.11-slim

# # Install system dependencies
# RUN apt-get update && \
#     apt-get install -y portaudio19-dev && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.AIStudio.txt .

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.Communify.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port available to the world outside this container
EXPOSE 4050

# Run the app with a production server
CMD ["streamlit", "Communify:app", "--bind", "0.0.0.0:4050"]