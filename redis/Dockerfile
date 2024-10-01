# Use the official Redis image
FROM redis:latest

# Copy the custom Redis configuration file
COPY redis.conf /usr/local/etc/redis/redis.conf

# Expose the Redis port (6379 by default)
EXPOSE 6379

# Run Redis with the custom configuration file
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

