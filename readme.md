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
