# Set working directory
WORKDIR /app

# Install Flask (and any other Python dependencies)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]
