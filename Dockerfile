# Base image for Python
FROM python:3.12-slim

# Install dependencies for Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Set working directory to root
WORKDIR /

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt gunicorn

# Copy the app directory into /app
COPY app /app

# Set PYTHONPATH to /app so Python finds the app module
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]
