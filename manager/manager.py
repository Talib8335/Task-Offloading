from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# List of fog nodes
fog_nodes = ['http://localhost:5000', 'http://localhost:5001', 'http://localhost:5002']

# Store fog node statuses
fog_node_statuses = {}

# Log file for manager actions
manager_log_file = "manager_log.json"

# Function to log manager actions
def log_manager_actions(action_data):
    with open(manager_log_file, 'a') as f:
        f.write(json.dumps(action_data) + "\n")


@app.route('/status_update', methods=['POST'])
def update_fog_node_status():
    """Receive status updates from fog nodes."""
    status_data = request.json
    fog_node_number = status_data['fog_node_number']
    fog_node_statuses[fog_node_number] = status_data
    print(f"Updated status from Fog Node {fog_node_number}: {status_data}")
    return jsonify({'status': 'updated'})


@app.route('/offload_task', methods=['POST'])
def offload_task():
    """Handle task offloading requests from IoT devices."""
    task = request.json
    best_fog_node = select_best_fog_node()

    if best_fog_node:
        # Forward the task to the selected fog node
        try:
            response = requests.post(best_fog_node + '/offload_task', json=task)
            task_result = response.json()

            # Log the task offloading to the manager's log file
            log_manager_actions({
                'task_type': task['task_type'],
                'task_size': task['task_size'],
                'deadline': task['deadline'],
                'fog_node': best_fog_node,
                'status': 'offloaded',
                'response': task_result
            })

            return task_result
        except Exception as e:
            log_manager_actions({
                'task_type': task['task_type'],
                'task_size': task['task_size'],
                'deadline': task['deadline'],
                'fog_node': best_fog_node,
                'status': 'failed',
                'error': str(e)
            })
            return jsonify({'status': 'error', 'message': f"Failed to offload to {best_fog_node}"}), 500
    else:
        log_manager_actions({
            'task_type': task['task_type'],
            'task_size': task['task_size'],
            'deadline': task['deadline'],
            'status': 'no_fog_available'
        })
        return jsonify({'status': 'error', 'message': 'No fog nodes available'}), 500


def select_best_fog_node():
    """Select the best fog node based on load (using a weighted algorithm)."""
    best_fog_node = None
    best_weight = float('inf')

    # Check each fog node status and calculate the load
    for fog_node, status in fog_node_statuses.items():
        weight = calculate_weight(status)
        fog_node_url = f"http://localhost:{status['port']}"
        if weight < best_weight:
            best_weight = weight
            best_fog_node = fog_node_url

    return best_fog_node


def calculate_weight(status):
    """Calculate the load weight for a fog node based on its current status."""
    return (0.6 * status['cpu_usage'] +
            0.3 * (1 - status['memory_available'] / status['total_memory']) * 100 +
            0.1 * status['task_queue_length'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
