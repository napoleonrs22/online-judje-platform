FROM python:3.10-slim

WORKDIR /app

# Install build tools and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (prefer binary wheels, fallback to source)
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt || \
    pip install --no-cache-dir --no-binary :all: -r requirements.txt

# Optional: install extra packages individually
RUN pip install --no-cache-dir 'bcrypt==4.0.1' 'passlib[bcrypt]==1.7.4'

# Copy app code
COPY . .

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
