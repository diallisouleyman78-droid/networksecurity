FROM python:3.10-slim-bookworm

WORKDIR /app

COPY . /app/

# Install dependencies (only if you REALLY need awscli)
RUN apt-get update && \
    apt-get install -y --no-install-recommends awscli && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]