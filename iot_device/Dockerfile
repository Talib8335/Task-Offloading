# Base Image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY device.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# No CMD specified since this service will run interactively
# and you want to control when it runs from the command line.
