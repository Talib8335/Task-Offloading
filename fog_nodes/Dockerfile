# Base Image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY fog_node1.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# No EXPOSE here as the port will be configured dynamically

# Command to run the fog node (Python script will read from environment variables)
CMD ["python", "fog_node1.py"]
