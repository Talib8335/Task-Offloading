# Base Image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY manager.py /app/
COPY requirements.txt /app/

# Install dependencies, including ping
RUN apt-get update && \
    apt-get install -y curl redis-tools iputils-ping && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port for the manager
EXPOSE 6000

# Command to run the manager
CMD ["python", "manager.py"]

#CMD ["/bin/sh"]