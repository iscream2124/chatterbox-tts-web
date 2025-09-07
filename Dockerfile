# Use Python 3.11 slim image (more stable)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Clone chatterbox repository
RUN git clone https://github.com/resemble-ai/chatterbox.git /app/chatterbox_repo

# Install chatterbox-tts
RUN pip install -e /app/chatterbox_repo

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p generated_audio templates static/css static/js

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app/chatterbox_repo:/app
ENV PORT=5000

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]