FROM python:3.11-slim

WORKDIR /app

# Copy all files first
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
