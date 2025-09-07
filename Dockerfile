# Use a Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for audio processing and Git
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone the chatterbox repository
RUN git clone https://github.com/resemble-ai/chatterbox.git /app/chatterbox_repo

# Install chatterbox-tts in editable mode
RUN pip install -e /app/chatterbox_repo

# Copy the Flask application files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app/chatterbox_repo:/app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
