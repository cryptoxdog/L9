FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY symbolic_computation/ ./symbolic_computation/
COPY tests/ ./tests/
COPY .env.example .env

# Create logs directory
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Run tests on build (optional)
# RUN pytest tests/ --cov=symbolic_computation

# Default command
CMD ["python", "-m", "pytest", "tests/"]
