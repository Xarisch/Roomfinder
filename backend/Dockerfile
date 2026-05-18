# Builder Stage
FROM python:3.11-slim as builder

WORKDIR /app

# Create a virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Runner Stage
FROM python:3.11-slim as runner

WORKDIR /app

RUN groupadd -r finder && useradd -r -g finder finder 

# Copy the entire virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set the PATH so the app uses the virtualenv's python and uvicorn
ENV PATH="/opt/venv/bin:$PATH"

COPY ./app /app
RUN chown -R finder:finder /app /opt/venv

USER finder

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]