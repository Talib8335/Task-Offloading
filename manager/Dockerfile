# Base Image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY manager.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the manager (but the actual port will be set in docker-compose.yml)
EXPOSE 6000

# Command to run the manager service
CMD ["python", "manager.py"]
