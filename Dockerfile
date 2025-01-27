# Base Python image
FROM python:3.11.10-slim

# Working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src ./src

# Expose the port
# EXPOSE 8080

# Run the main script
CMD ["python", "src/main.py"]
