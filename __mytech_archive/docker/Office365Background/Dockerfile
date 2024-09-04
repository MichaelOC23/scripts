# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CLIENT_ID=PLACEHOLDER
ENV TENANT_ID=PLACEHOLDER
ENV OFFICE365_BACKGROUND_PORT=PLACEHOLDER

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt first, to leverage Docker cache
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 4001

# Run the Flask application
CMD ["python", "Office365Background.py"]

# For Reference: Docker Build Command
# docker build -t Office365Background-app .

# For Reference: Docker Run Command
# docker run -d -p 4001:4001 --name Office365Background-Container \
#     -e CLIENT_ID=$CLIENT_ID \
#     -e TENANT_ID=$TENANT_ID \
#     Office365Background-app