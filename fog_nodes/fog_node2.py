import os
import psutil
import requests
import time
import threading
import csv
from flask import Flask, jsonify, request
import redis
from datetime import datetime

app = Flask(__name__)

# Set fog node number and port from environment variables
fog_node_number = os.getenv('FOG_NODE_NUMBER', 2)  # Change for each node
port = int(os.getenv('PORT', 5001))  # Change for each node

# Get Redis host and port from environment variables (default to 'redis_cache' and port 6379)
redis_host = os.getenv('REDIS_HOST', 'redis_cache')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Establish Redis connection
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
            'from_cache': True,
            'delay': 0,
            'energy_consumption': 0,
            'result': result,
            'cache_hit': True
        }
        log_task_metrics_csv(task_metrics)
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
        'cache_hit': False
    }

    log_task_metrics_csv(task_metrics)
    return jsonify(task_metrics)


def process_task(task):
    """Simulate task processing and calculate delay and energy consumption."""
    current_tasks.append(task)
    
    # Simulate delays
    transmission_delay = task['task_size'] / 10
    propagation_delay = 0.1
    processing_time = task['task_size'] / 10

    time.sleep(processing_time)  # Simulate processing

    total_delay = transmission_delay + propagation_delay + processing_time
    energy_consumption = total_delay * psutil.cpu_percent() * 0.5

    current_tasks.pop()

    return total_delay, energy_consumption

def send_status_to_manager():
    """Send the fog node's status to the central manager periodically."""
    update_interval = 20 # Default interval for sending status updates
    max_retries = 3  # Maximum number of retries in case of failure
    retry_delay = 5  # Delay between retries in case of failure

    while True:
        cpu_usage = psutil.cpu_percent(interval=2)
        memory_info = psutil.virtual_memory()
        task_queue_length = len(current_tasks)

        status_data = {
            'fog_node_number': fog_node_number,
            'cpu_usage': cpu_usage,
            'memory_available': memory_info.available,
            'total_memory': memory_info.total,
            'task_queue_length': task_queue_length,
            'port': port,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        success = False
        for attempt in range(max_retries):
            try:
                # Send status to manager
                response = requests.post(f'http://manager:6000/status_update', json=status_data)
                if response.status_code == 200:
                    success = True
                    break  # Exit the retry loop on success
            except Exception as e:
                print(f"Error sending status update, attempt {attempt + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if not success:
            print(f"Failed to send status update after {max_retries} attempts. Will try again after {update_interval} seconds.")

        time.sleep(update_interval)  # Regular update interval




if __name__ == "__main__":
    status_thread = threading.Thread(target=send_status_to_manager)
    status_thread.daemon = True
    status_thread.start()

    app.run(host='0.0.0.0', port=port, debug=True)

