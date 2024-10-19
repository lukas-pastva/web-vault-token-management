FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Set environment variables (you can also pass these when running the container)
ENV VAULT_ADDR=http://vault:8200
# ENV VAULT_TOKEN=your_vault_token_here  # It's recommended to pass this securely

# Run the application
CMD ["python", "app.py"]
