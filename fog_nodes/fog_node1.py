import os
import psutil
import requests
import time
import threading
import csv
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

# Set fog node number and port from environment variables
fog_node_number = os.getenv('FOG_NODE_NUMBER', 1)  # Default to node 1 if not set
port = int(os.getenv('PORT', 5000))  # Default to port 5000 if not set

# Get Redis host and port from environment variables (default to 'localhost' and port 6379)
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Establish Redis connection with retry logic
cache = None
while cache is None:
    try:
        cache = redis.Redis(host=redis_host, port=redis_port)
        cache.ping()  # Test connection to Redis
        print(f"Connected to Redis at {redis_host}:{redis_port}")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis. Retrying... {e}")
        time.sleep(5)  # Retry every 5 seconds

# Simulate a task queue
current_tasks = []

log_file = f"fog_node_{fog_node_number}_log.csv"  # CSV Log file for task metrics

# CSV Logging
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['task_id', 'fog_node_number', 'from_cache', 'delay', 'energy_consumption', 'result', 'cache_hit'])


# Function to log metrics to CSV file
def log_task_metrics_csv(metrics):
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([metrics['task_id'], metrics['fog_node_number'], metrics['from_cache'], metrics['delay'],
                         metrics['energy_consumption'], metrics['result'], metrics['cache_hit']])


@app.route('/offload_task', methods=['POST'])
def offload_task():
    """Receive and process a task, checking Redis cache first."""
    task = request.json
    task_id = f"{task['task_type']}_{task['task_size']}"

    # Check Redis cache for the task result
    cached_result = cache.get(task_id)
    if cached_result:
        result = cached_result.decode()
        task_metrics = {
            'task_id': task_id,
            'fog_node_number': fog_node_number,
            'from_cache': True,  # Indicate that it was fetched from cache
            'delay': 0,
            'energy_consumption': 0,
            'result': result,
            'cache_hit': True  # Log cache hit
        }
        log_task_metrics_csv(task_metrics)
        print(f"Task {task['task_type']} fetched from cache. (Task ID: {task_id})")
        return jsonify(task_metrics)

    # Simulate processing the task and calculate all delays
    total_delay, energy_consumption = process_task(task)

    result = f"Processed {task['task_type']} on fog node {fog_node_number}"

    # Cache result with expiration (TTL of 10 minutes)
    cache.set(task_id, result, ex=600)

    task_metrics = {
        'task_id': task_id,
        'fog_node_number': fog_node_number,
        'from_cache': False,
        'delay': total_delay,
        'energy_consumption': energy_consumption,
        'result': result,
        'cache_hit': False  # Log cache miss
    }

    log_task_metrics_csv(task_metrics)
    print(f"Task {task['task_type']} processed in {total_delay:.2f} seconds, energy used: {energy_consumption:.2f} units")
    return jsonify(task_metrics)


def process_task(task):
    """Simulate task processing and calculate delay and energy consumption."""
    current_tasks.append(task)
    start_time = time.time()

    # Simulate queuing delay
    queuing_delay = len(current_tasks) * 0.5  # Example: 0.5 seconds per task in queue

    # Simulate transmission delay (based on task size and bandwidth)
    transmission_delay = task['task_size'] / 10  # Simplified: 1 unit time per 10MB

    # Simulate propagation delay
    propagation_delay = 0.1  # Assume a small propagation delay (e.g., 0.1 seconds)

    # Simulate processing delay
    processing_time = task['task_size'] / 10  # Simplified processing time

    # Capture CPU usage before and after processing
    cpu_start = psutil.cpu_percent(interval=None)

    # Simulate actual processing time
    time.sleep(processing_time)

    cpu_end = psutil.cpu_percent(interval=None)

    # Calculate total delay and energy consumption
    total_delay = queuing_delay + transmission_delay + propagation_delay + processing_time
    avg_cpu_usage = (cpu_start + cpu_end) / 2
    energy_consumption = total_delay * avg_cpu_usage * 0.5  # Energy in arbitrary units

    current_tasks.pop()

    return total_delay, energy_consumption


def send_status_to_manager():
    """Send the fog node's status to the central manager periodically."""
    while True:
        # Collect resource usage data (CPU, memory, etc.)
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        task_queue_length = len(current_tasks)

        # Send status to the manager
        status_data = {
            'fog_node_number': fog_node_number,
            'cpu_usage': cpu_usage,
            'memory_available': memory_info.available,
            'total_memory': psutil.virtual_memory().total,
            'task_queue_length': task_queue_length,
            'port': port
        }

        try:
            response = requests.post('http://localhost:6000/status_update', json=status_data)
            if response.status_code != 200:
                print(f"Failed to update status: {response.status_code}")
        except Exception as e:
            print(f"Error sending status update: {e}")

        time.sleep(10)  # Send status every 10 seconds


# Start the status update thread when the fog node starts
if __name__ == "__main__":
    status_thread = threading.Thread(target=send_status_to_manager)
    status_thread.daemon = True
    status_thread.start()

    app.run(host='0.0.0.0', port=port)
