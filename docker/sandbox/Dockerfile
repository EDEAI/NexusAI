FROM python:3.12.10

# Use network proxy as needed
# ARG HTTP_PROXY=http://192.168.6.249:10809
# ARG HTTPS_PROXY=http://192.168.6.249:10809

# Set proxy environment variables for build process
# ENV HTTP_PROXY=${HTTP_PROXY}
# ENV HTTPS_PROXY=${HTTPS_PROXY}
# ENV http_proxy=${HTTP_PROXY}
# ENV https_proxy=${HTTPS_PROXY}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    firejail \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv - high-performance Python package manager
RUN pip install --no-cache-dir uv

# Install FastAPI dependencies
RUN pip install --no-cache-dir fastapi uvicorn jinja2

# Clear proxy environment variables (optional, for security)
# ENV HTTP_PROXY=""
# ENV HTTPS_PROXY=""
# ENV http_proxy=""
# ENV https_proxy=""

# Create virtual environment cache directory
RUN mkdir -p /app/venv_cache

# Set working directory
WORKDIR /docker/sandbox

# Copy the API server script
COPY ./api_server.py /docker/sandbox

# Run the application
CMD ["python", "api_server.py"]