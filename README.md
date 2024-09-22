task_offloading_project/
│
├── iot_device/
│   ├── device.py  # IoT device sends tasks to the manager
│   ├── Dockerfile
│   ├── requirements.txt  # Dependencies for IoT device
│
├── fog_nodes/
│   ├── fog_node1.py  # Fog node 1
│   ├── fog_node2.py  # Fog node 2
│   ├── fog_node3.py  # Fog node 3
│   ├── Dockerfile
│   ├── requirements.txt  # Dependencies for fog nodes
│
├── manager/
│   ├── manager.py  # Centralized manager for task distribution
│   ├── Dockerfile
│   ├── requirements.txt  # Dependencies for the manager
│
├── redis/  # Redis cache setup
│   ├── Dockerfile
│   ├── requirements.txt  # Dependencies for Redis setup (if needed)
│
├── docker-compose.yml  # For orchestration
├── README.md  # Project documentation
