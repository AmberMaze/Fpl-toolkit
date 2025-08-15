FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy everything needed for build (LICENSE + src included)
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install '.[web,ai]'

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["sh","-c","python -m fpl_toolkit.cli serve --host 0.0.0.0 --port ${PORT:-8000}"]
