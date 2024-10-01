import numpy as np
import requests
import random
import time
from datetime import datetime, timedelta


manager_url = 'http://manager:6000'

task_types = ["image_processing", "data_analysis", "video_streaming"]


# Define rate-limiting parameters
task_limit = 5  # Maximum number of tasks that can be offloaded per minute
tasks_sent = 0
last_reset_time = datetime.now()

def generate_task():
    task = {
        'task_type': random.choice(task_types),
        'task_size': random.randint(10, 100),
        'deadline': random.randint(5, 30)
    }
    return task

def send_task_to_manager(task):
    try:
        network_delay = task['task_size'] / 100  # Simplified network delay
        response = requests.post(f'http://manager:6000/offload_task', json=task)
        if response.status_code == 200:
            result = response.json()
            result['network_delay'] = network_delay
            return result
        else:
            print(f"Failed to offload task: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error communicating with manager: {e}")
        return None



def run():
    global tasks_sent, last_reset_time

    while True:
        # Reset the task counter every minute
        if datetime.now() > last_reset_time + timedelta(minutes=1):
            tasks_sent = 0
            last_reset_time = datetime.now()

        # Check if we can send more tasks
        if tasks_sent < task_limit:
            task = generate_task()
            print(f"Generated task: {task}")
            result = send_task_to_manager(task)
            if result:
                print(f"Task processed by fog node {result['fog_node_number']}: {result}")
            else:
                print("Task could not be processed.")

            tasks_sent += 1
        else:
            print("Task limit reached. Waiting for the next cycle.")

        # Random wait time between task generations
        wait_time = np.random.poisson(lam=5)
        time.sleep(wait_time)


if __name__ == "__main__":
    run()
