# Use a lightweight Python image as the base
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install build dependencies for pycairo and other potential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libcairo2-dev \
        libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . .

# Expose the port the Flask app runs on
EXPOSE 8080

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
# In a production environment, this should point to a service account key file
# mounted into the container or handled by workload identity.
# For local testing, this can be set to a local path or omitted if running on GCP.
# ENV GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json

# Command to run the application
# Use Gunicorn or another production-ready WSGI server in a real application
# For simplicity, we'll use Flask's built-in server here, but it's not recommended for production
CMD ["python", "app.py"]
