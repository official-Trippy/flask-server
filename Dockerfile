# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port 5000 (or any other port your Flask app is running on)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]
