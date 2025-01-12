# Base Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary directories and files
COPY app.py .
COPY tests.py .
COPY templates/ templates/
COPY static/ static/

# Create upload directory if it doesn't exist
RUN mkdir -p static/images

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]