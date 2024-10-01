from flask import Flask, request, jsonify
import requests
import json
import logging
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# List of fog nodes with predefined URLs and ports
fog_nodes = [
    {'url': 'http://fog_node1:5000', 'port': 5000},
    {'url': 'http://fog_node2:5001', 'port': 5001},
    {'url': 'http://fog_node3:5002', 'port': 5002}
]

# Store fog node statuses
fog_node_statuses = {}

# Define how long to consider a fog node's status as valid
STATUS_TIMEOUT_SECONDS = 30  # Keep statuses for 30 seconds

# Log file for manager actions
manager_log_file = "manager_log.json"

# Configure logging to print both to console and file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[
                        logging.FileHandler("manager_debug.log"),
                        logging.StreamHandler()  # This prints to console
                    ])


# Function to log manager actions in JSON format
def log_manager_actions(action_data):
    with open(manager_log_file, 'a') as f:
        f.write(json.dumps(action_data) + "\n")


@app.route('/status_update', methods=['POST'])
def update_fog_node_status():
    """Receive status updates from fog nodes."""
    status_data = request.json
    fog_node_number = status_data['fog_node_number']

    # Record the current timestamp
    status_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update the status dictionary with fog node status
    fog_node_statuses[fog_node_number] = status_data

    logging.info(f"Received status update from Fog Node {fog_node_number}: {status_data}")

    # Print to console
    print(f"Status received from Fog Node {fog_node_number}: {status_data}")

    return jsonify({'status': 'updated'})


@app.route('/offload_task', methods=['POST'])
def offload_task():
    """Handle task offloading requests from IoT devices."""
    task = request.json
    logging.info(f"Received task for offloading: {task}")

    # Print to console
    print(f"Task received for offloading: {task}")

    best_fog_node = select_best_fog_node()

    if best_fog_node:
        try:
            logging.info(f"Selected fog node for offloading: {best_fog_node['url']}")
            print(f"Sending task to fog node {best_fog_node['url']}...")

            response = requests.post(best_fog_node['url'] + '/offload_task', json=task)

            if response.status_code == 200:
                task_result = response.json()
                log_manager_actions({
                    'task_type': task['task_type'],
                    'task_size': task['task_size'],
                    'deadline': task['deadline'],
                    'fog_node': best_fog_node['url'],
                    'status': 'offloaded',
                    'response': task_result
                })
                logging.info(f"Successfully offloaded task to {best_fog_node['url']}: {task_result}")

                # Print to console
                print(f"Task successfully offloaded to Fog Node {best_fog_node['url']}. Response: {task_result}")

                return task_result
            else:
                raise Exception(
                    f"Failed to offload task. Status code: {response.status_code}, Response: {response.text}")

        except Exception as e:
            logging.error(f"Error during task offloading: {str(e)}")
            log_manager_actions({
                'task_type': task['task_type'],
                'task_size': task['task_size'],
                'deadline': task['deadline'],
                'fog_node': best_fog_node['url'],
                'status': 'failed',
                'error': str(e)
            })
            print(f"Error offloading task to Fog Node {best_fog_node['url']}: {e}")
            return jsonify(
                {'status': 'error', 'message': f"Failed to offload to {best_fog_node['url']}. Error: {str(e)}"}), 500
    else:
        logging.warning("No available fog nodes to offload task.")
        log_manager_actions({
            'task_type': task['task_type'],
            'task_size': task['task_size'],
            'deadline': task['deadline'],
            'status': 'no_fog_available'
        })
        print("No available fog nodes for offloading.")
        return jsonify({'status': 'error', 'message': 'No fog nodes available'}), 500


def select_best_fog_node():
    best_fog_node = None
    best_weight = float('inf')
    current_time = datetime.now()

    for fog_node in fog_nodes:
        fog_node_number = str(fog_node['port'] - 4999)  # Map port to string fog node number
        status = fog_node_statuses.get(fog_node_number)  # Retrieve the status using the correct fog node number

        if status:
            try:
                # Parse the timestamp from the fog node's status update
                status_timestamp = datetime.strptime(status['timestamp'], '%Y-%m-%d %H:%M:%S')
                time_diff = (current_time - status_timestamp).total_seconds()

                # Only consider fog nodes whose status update is within the time limit
                if time_diff <= STATUS_TIMEOUT_SECONDS:
                    weight = calculate_weight(status)
                    print(f"Fog Node {fog_node['url']} has weight: {weight}, Status: {status}")
                    if weight < best_weight:
                        best_weight = weight
                        best_fog_node = fog_node
                else:
                    print(f"Fog Node {fog_node['url']} has outdated status (last update {time_diff} seconds ago).")
            except KeyError as e:
                print(f"Error: Missing key in status data: {e}")
        else:
            print(f"No status available for Fog Node {fog_node['url']}")

    if best_fog_node is None:
        print(f"No suitable fog node found. All weights: {[calculate_weight(status) for status in fog_node_statuses.values()]}")

    return best_fog_node



def calculate_weight(status):
    try:
        return (0.4 * status['cpu_usage'] +  # Lower CPU impact
                0.4 * (1 - status['memory_available'] / status['total_memory']) * 100 +  # More emphasis on memory
                0.2 * status['task_queue_length'])  # Keep task queue weight same
    except KeyError as e:
        logging.error(f"Error in calculating weight due to missing key: {e}")
        return float('inf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
