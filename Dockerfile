# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for SQLite (fallback for local testing)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Make startup script executable
RUN chmod +x startup.sh

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Run the startup script
CMD ["./startup.sh"]

