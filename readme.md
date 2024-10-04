# Task Offloading System

## Overview
This repository contains the implementation of a task offloading system designed for IoT devices, leveraging fog and cloud nodes. The system dynamically selects the best node for task offloading using a **Weighted Formula Method**. The goal is to improve performance and reduce latency with the help of Redis caching. The entire project is containerized using Docker for easy deployment and management.

## Workflow
1. **IoT Device Layer**: IoT devices generate tasks and submit them to the manager.
2. **Manager**: The manager receives tasks from IoT devices and evaluates the status of all fog nodes (checking CPU usage, memory usage, task queue length, etc.). Based on the **Weighted Formula Method**, it selects the most suitable fog node for task offloading.
3. **Fog Nodes**: Fog nodes process tasks based on their resource availability. If selected, the node handles the task processing; otherwise, it communicates with the manager for further decision-making. Redis caching is utilized to store frequently requested tasks.
4. **Cloud Node**: If none of the fog nodes are available, tasks are forwarded to the cloud node for processing.
5. **Redis Cache**: Frequently accessed tasks are cached using Redis, reducing the processing time and server load for repeated tasks.

## Task Offloading Details
1. **Task Generation**: IoT devices generate tasks with varying characteristics, such as size and priority. The task generation follows a **Poisson 
                         distribution** to simulate real-world randomness.
2. **Task Submission**: Tasks are sent to the manager, which checks all fog nodes for resource availability.
3. **Fog Node Selection Using Weighted Formula Method**:  
   - The manager evaluates each fog node based on the following parameters:
     - **CPU Usage**
     - **Memory Usage**
     - **Task Queue Length**
     - **Network Delay**
     - **Energy Consumption**
   - Using a weighted formula, the node with the best score is selected for task offloading. If no suitable fog node is found, the task is forwarded to the cloud.
4. **Task Processing**: The selected fog or cloud node processes the task using its available resources. Redis caches frequently accessed tasks to speed up future processing.

## Redis Caching
Redis is integrated into the system to store frequently requested tasks. If a task is found in the Redis cache, it is fetched directly, avoiding the need for reprocessing. This reduces latency and server load, significantly improving the overall system performance.

## Performance Testing
We have extensively tested the overall performance of each container in the system (IoT devices, fog nodes, cloud node, and Redis) to monitor:
- **CPU usage**
- **Memory usage**
- **Disk I/O**
- **Network usage**

### Testing Tools:
We used various tools to monitor container metrics such as `Docker stats`, `htop`, and `psutil` to gather CPU, memory, and I/O metrics.


## Project Structure

```plaintext

Task_offloading/
│
├── iot_device/
│   ├── device.py  
│   ├── Dockerfile
│   ├── requirements.txt  
│
├── fog_nodes/
│   ├── fog_node1.py  
│   ├── fog_node2.py  
│   ├── fog_node3.py  
│   ├── Dockerfile
│   ├── requirements.txt  
│
├── manager/
│   ├── manager.py  # Centralized manager for task distribution
│   ├── Dockerfile
│   ├── requirements.txt  
│
├── redis/  # Redis cache setup
│   ├── Dockerfile
│   ├── requirements.txt  
│
├── docker-compose.yml  # For orchestration
├── README.md 

```
## Setup Instructions

### Prerequisites
- Docker
- Docker Compose
- Python 3.8 or higher

### Steps to Setup and Run the System
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Talib8335/Task-Offloading.git
   cd Task-Offloading
   install dependencies pip install -r requirements.txt
   
   ```

2. **Build Docker Images:**
   ```bash
      docker compose build
     ```
3. **Start the Services:**
   ```bash
     docker compose up -d
     ```
   
4. **Access the Containers:**
  ```bash
   #IoT device container:
   docker exec -it iot_device /bin/bash

  # Fog Node 1:
  docker exec -it fog_node_1 /bin/bash  #similarly for fog_node2 & fog_node3

  # Cloud Node:
   docker exec -it cloud_node /bin/bash
   ```

5. **View logs of a specific container:**
     ```bash
     sudo docker compose logs -f <container_name> #example - fog_node1
     ```

6. **Stop the Services:**
   ```bash
   docker-compose down
   ```

### Snapshots:
Below are snapshots showing the performance metrics of the system:

### Snapshots for Individual Containers

- **Fog Node 1**:
  ![Fog Node 1 CPU & Memory Usage](./mnt/data/fog1.png)

- **Manager**:
  ![Manager CPU & Memory Usage](./mnt/data/manager.png)

### Combined Performance Results:
These snapshots represent the combined performance metrics across all containers.

- **Overall CPU Usage:**
  ![Combined CPU Usage](./mnt/data/Screenshot from 2024-10-04 22-32-22.png)

- **Memory, I/O, and Network Usage:**
  ![Combined Memory & I/O](./mnt/data/Screenshot from 2024-10-04 22-30-32.png)

- **Container List:**
  ![Container Overview](./mnt/data/Screenshot from 2024-10-04 22-20-45.png)

### Terminal Output
Below is a terminal view showing the task processing across all containers.

![Terminal View of Task Offloading](./mnt/data/Screenshot from 2024-10-04 22-18-47.png)


![1000034988](https://github.com/user-attachments/assets/4654aeb5-4bf3-4799-b9fd-f474b73ba5d6)
![1000034987](https://github.com/user-attachments/assets/3d8e98e5-dde5-4472-92e7-3a2408d40ddb)
![1000034990](https://github.com/user-attachments/assets/3d706bd1-f3dd-4852-bb38-e093b2511c11)
![1000034993](https://github.com/user-attachments/assets/db804653-2f10-4c8a-9040-02b7d27019e7)
![1000035015](https://github.com/user-attachments/assets/b066e2ed-895c-441d-9299-96d84851cee0)
![1000035014](https://github.com/user-attachments/assets/084c7bb4-e6bb-45f4-8926-b2ce66b8b1c1)
![1000035016](https://github.com/user-attachments/assets/7dc31b12-8ac6-44c4-97f2-35fc14238ee0)
![1000035013](https://github.com/user-attachments/assets/93ea0d6b-f1b3-486b-94dd-225f7b3dbf1f)
![1000035011](https://github.com/user-attachments/assets/8a59ba9e-fba9-4551-a7cb-16855884e20b)
![1000035012](https://github.com/user-attachments/assets/c40d53cb-ef7e-4730-9f67-d13605cc67a0)
![1000035010](https://github.com/user-attachments/assets/9ab1aa67-c95b-4167-896a-4981def02658)
![1000035009](https://github.com/user-attachments/assets/dc471131-08e4-4a56-b654-13a930bfafd9)
![1000035008](https://github.com/user-attachments/assets/51aea0aa-258a-455d-91c5-338b5972e6fc)
![1000035007](https://github.com/user-attachments/assets/80a215d2-3293-44af-af8e-b3e503eef0ea)
![1000035006](https://github.com/user-attachments/assets/2476ebc2-9ccb-42e5-bc0e-e81f89d935c3)


