# Base Image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy necessary files (only one fog node script is used based on FOG_NODE_NUMBER)
COPY fog_node1.py /app/
COPY fog_node2.py /app/
COPY fog_node3.py /app/
COPY requirements.txt /app/

# Install dependencies, including ping
RUN apt-get update && \
    apt-get install -y curl iputils-ping && \
    pip install --no-cache-dir -r requirements.txt

# Expose port based on fog node number
EXPOSE ${PORT}

# Command to run the fog node based on environment variable
CMD ["sh", "-c", "python fog_node${FOG_NODE_NUMBER}.py"]

