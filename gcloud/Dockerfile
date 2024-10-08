FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only the requirements.txt file first, to cache dependencies separately
COPY requirements.gcloud.txt /app/

# Install Python dependencies and cache the result
RUN pip install --no-cache-dir -r requirements.gcloud.txt

# Now copy the rest of the application
COPY . /app


# Define the build argument for the OAuth credential
ARG COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL

# Set the environment variable inside the container
ENV COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL=${COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL}

# Expose port 8080
EXPOSE 8080

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
