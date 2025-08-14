FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install '.[web]'

# Copy source code
COPY src ./src

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "fpl_toolkit.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]