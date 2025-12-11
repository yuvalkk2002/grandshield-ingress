FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if needed (e.g. for audio processing libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libasound2-dev && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml for dependency installation
COPY pyproject.toml .

# Install dependencies using uv
# --system installs into the system python environment
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Copy application code
COPY . .

# Install the project itself (if needed, or just let python find it in CWD)
# This installs the project in editable mode or just as a package, ensuring 'app' is importable if intended to be installed
RUN uv pip install --system --no-deps .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Expose the port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]