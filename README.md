# **NexusAI: The Future of Intelligent Collaboration**


> **Redefining Team Collaboration:**  
> An open-source platform that fuses human and AI capabilities to achieve task automation, intelligent decision-making, and full-process visualization, unlocking limitless productivity and driving organizations toward a smarter future.

---

## **Features**

### 🎯 **Core Features**
- **Task Automation**: Use intelligent agents to break down and execute tasks, minimizing repetitive work.
- **Workflow Management**: A modular workflow designer supports multi-step task flows for complex business scenarios.
- **Real-Time Collaboration**: Seamless integration of humans and AI agents to boost team efficiency.
- **Global Transparency**: Dashboards provide complete oversight of task progress, resource allocation, and team activity.

### 🌟 **Modular Innovation**
- **Agent Customization**: Easily create versatile agents for various use cases.
- **Workflow Design**: Drag-and-drop workflow nodes to implement complex logic quickly.
- **Knowledge Base Support**: Integrate multiple document formats and automatically parse content for agent use.
- **Skill Expansion**: Custom Python scripting for flexible solutions to specific needs.


There are two deployment methods: docker compose deployment and source code deployment

# Docker Compose deployment

## Prerequisites
See [Install Docker](https://docs.docker.com/engine/install/) and [Install Docker Compose](https://docs.docker.com/compose/install/) to complete the Docker and Docker Compose installation. Use the `docker-compose` or `docker compose` command depending on your Docker Compose version.
See [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to enable GPU support in Docker containers.

## Clone NexusAI
Clone the NexusAI source code to your local environment
```bash
git clone https://github.com/EDEAI/NexusAI.git
```

## Initialize the model directory and storage directory
```bash
cd NexusAI
mkdir -p models storage
chmod 777 storage
```

## Cloning the Embedding and Reranker models for offline mode
```bash
# Enter the model directory
cd models

# Clone all models
apt install git-lfs
git clone https://huggingface.co/GanymedeNil/text2vec-large-chinese
git clone https://huggingface.co/BAAI/bge-reranker-v2-m3
```

## Milvus Authentication
If you want to enable Milvus authentication, refer to [Milvus Authentication](https://milvus.io/docs/authenticate.md) to set up Milvus authentication and modify the milvus-standalone service settings in `docker-compose.yml`

## Launch NexusAI
Enter the Docker directory of the NexusAI source code
```bash
cd NexusAI/docker
```

Copy `docker-compose.yml` and replace `SANDBOX_HOST` with the real IP address of the host
```bash
cp docker-compose.yml.template docker-compose.yml
```

Start all Docker containers
```bash
docker-compose up -d
```

After running the command, you should see output similar to the following, showing the status of all containers
```bash
[+] Running 11/11
 ✔ Network docker_my_network         Created                   0.1s 
 ✔ Container docker-web-1            Started                   1.5s 
 ✔ Container docker-redis-1          Started                   1.3s 
 ✔ Container milvus-minio            Started                   1.3s 
 ✔ Container docker-sandbox-1        Started                   1.8s 
 ✔ Container milvus-etcd             Started                   1.3s 
 ✔ Container docker-mysql-1          Started                   1.8s 
 ✔ Container milvus-standalone       Started                   1.9s 
 ✔ Container docker-celery-1         Started                   2.5s 
 ✔ Container docker-multi_service-1  Started                   2.5s 
 ✔ Container docker-nginx-1          Started                   0.8s
```

Finally, you can check whether all containers are running normally
```bash
docker-compose ps
```

In the output below, you can see three business service containers `celery` `multi_service` `web`, and the rest are basic service containers
```bash
NAME                     IMAGE                                      COMMAND                  SERVICE             CREATED              STATUS                                 PORTS
docker-celery-1          edeai/celery:0.0.1                         "python celery_app.py"   celery              About a minute ago   Up About a minute                      
docker-multi_service-1   edeai/multi_service:0.0.1                  "sh -c 'python docke…"   multi_service       About a minute ago   Up About a minute                      
docker-mysql-1           mysql:8.0                                  "docker-entrypoint.s…"   mysql               About a minute ago   Up About a minute                      33060/tcp, 0.0.0.0:9461->3306/tcp, [::]:9461->3306/tcp
docker-nginx-1           nginx:latest                               "/docker-entrypoint.…"   nginx               About a minute ago   Up About a minute                      0.0.0.0:9470->80/tcp, [::]:9470->80/tcp
docker-redis-1           redis:6.2                                  "docker-entrypoint.s…"   redis               About a minute ago   Up About a minute                      0.0.0.0:9462->6379/tcp, [::]:9462->6379/tcp
docker-sandbox-1         edeai/sandbox:0.0.1                        "python api_server.py"   sandbox             About a minute ago   Up About a minute                      0.0.0.0:9464->8001/tcp, [::]:9464->8001/tcp
docker-web-1             edeai/web:0.0.1                            "docker-entrypoint.s…"   web                 About a minute ago   Up About a minute                      
milvus-etcd              quay.io/coreos/etcd:v3.5.5                 "etcd -advertise-cli…"   etcd                About a minute ago   Up About a minute (healthy)            2379-2380/tcp
milvus-minio             minio/minio:RELEASE.2023-03-20T20-16-18Z   "/usr/bin/docker-ent…"   minio               About a minute ago   Up About a minute (healthy)            9000/tcp
milvus-standalone        milvusdb/milvus:v2.3.1                     "/tini -- milvus run…"   milvus-standalone   About a minute ago   Up About a minute (health: starting)   0.0.0.0:9463->19530/tcp, [::]:9463->19530/tcp
```

## Visit NexusAI
After all containers are fully started, visit the following URL to enter the NexusAI homepage
```http
http://127.0.0.1:9470
```

When you visit for the first time, you can log in using the following initial administrator account
```
Email:
admin@nexusai.com

Password:
nexusaipwd
```

Note that the initial administrator password is updated through the environment variable `INIT_ADMIN_PASSWORD` in `docker-compose.yml`

## Pull NexusAI
Please execute the commands in the following order:
1. Enter the Docker directory of the NexusAI source code
2. Stop all containers
3. Pull the updated content from the git repository, and make sure to synchronize the updated content in `docker-compose.yml.template` to `docker-compose.yml`
4. Start all containers
```bash
cd NexusAI/docker
docker-compose down
git pull origin main
docker-compose up -d
```

## Custom Configuration
Edit the environment variables and service configuration in `docker-compose.yml` and restart NexusAI
```bash
cd NexusAI/docker
docker-compose down
docker-compose up -d
```

## docker-compose.yml configuration instructions
Backend environment variables
```yaml
# MySQL related configuration
MYSQL_HOST: mysql
MYSQL_PORT: 3306
MYSQL_USER: nexus_ai
MYSQL_PASSWORD: mysqlpwd
MYSQL_DB: nexus_ai

# Redis related configuration
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_DB: 0
REDIS_PASSWORD: redispwd

# websocket message queue key
WEBSOCKET_MESSAGE_QUEUE_KEY: websocket_message_queue

# Vector database related configuration
VDB_TYPE: Milvus
VDB_HOST: milvus-standalone
VDB_PORT: 19530
VDB_USER: root
VDB_PASSWORD: milvuspwd

# Vector database retriever configuration
# Vector database retriever class in langchain, number of retriever paragraphs returned, and retriever paragraph score threshold
RETRIEVER_TYPE: VectorStoreRetriever
RETRIEVER_K: 4
RETRIEVER_SCORE_THRESHOLD: 0

# The encryption key and expiration time of the access token
ACCESS_TOKEN_SECRET_KEY: nexus_ai
ACCESS_TOKEN_EXPIRE_MINUTES: 14400

# logging related configuration
LOG_ROTATE_INTERVAL: 6
LOG_BACKUP_COUNT: 20

# http related configuration
HTTP_CONNECT_TIMEOUT: 300
HTTP_READ_TIMEOUT: 600
HTTP_WRITE_TIMEOUT: 600
HTTP_RESPONSE_MAX_BINARY_SIZE: 10485760
HTTP_RESPONSE_MAX_TEXT_SIZE: 1048576

# Sandbox service connection configuration and workers number configuration
SANDBOX_HOST: 127.0.0.1
SANDBOX_PORT: 9464
SANDBOX_FASTAPI_WORKERS: 2

# Default configuration for LLM model
# Default supplier configuration ID (corresponding to the primary key of the supplier_configurations data table)
# Default LLM model configuration ID (corresponding to the primary key of the model_configurations data table)
DEFAULT_LLM_SUPPLIER_CONFIG_ID: 1
DEFAULT_LLM_CONFIG_ID: 3

# API, websocket and meeting room websocket service port configuration
API_PORT: 9472
WEBSOCKET_PORT: 9473
CHATROOM_WEBSOCKET_PORT: 9474

# Web access address
WEB_URL: http://127.0.0.1:9470

# Backend icon resource access address
ICON_URL: http://127.0.0.1:9470

# Agent/workflow API access timeout
APP_API_TIMEOUT: 60

# Number of api service workers
FASTAPI_WORKERS: 2

# Number of celery service workers
CELERY_WORKERS: 4

# Initial administrator password. After changing this configuration, restart NexusAI to take effect.
INIT_ADMIN_PASSWORD: nexusaiadmin
```

Front-end environment variables
```yaml
# Backend API service access address
WEB_API_URL: http://127.0.0.1:9470
# Backend websocket service address (except meeting room service)
WEB_WS_URL: ws://127.0.0.1:9470/ws
# Backend meeting room service websocket service address
WEB_CHAT_URL: ws://127.0.0.1:9470/ws_chat
```

# Source code deployment

## Prerequisites
Before deploying NexusAI locally, we need to deploy the following basic services:
1. [Docker](https://docs.docker.com/engine/install/)
2. [nginx](https://nginx.org/en/docs/install.html)
3. [MySQL](https://dev.mysql.com/doc/refman/8.0/en/installing.html)
4. [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
5. [Milvus](https://milvus.io/docs/install_standalone-docker-compose.md)
6. [Anaconda](https://docs.anaconda.com/anaconda/install/)
7. [Node.js (>=20.0)](https://nodejs.org/en/download/package-manager)

[Clone the NexusAI source code to your local environment](#clone-nexusai)

## Milvus Authentication
If you want to enable Milvus authentication, refer to [Milvus Authentication](https://milvus.io/docs/authenticate.md) to set up Milvus authentication.

## Server deployment
[Initialize the model directory and storage directory](#initialize-the-model-directory-and-storage-directory)

[Cloning the Embedding and Reranker models for offline mode](#cloning-the-embedding-and-reranker-models-for-offline-mode)

Initialize the database, If your MySQL version is >= 8.0, you need to add "mysql_native_password=ON" to the MySQL configuration file.
```bash
cd NexusAI

# Login to mysql
mysql -u root -p

# Create a database, user, and grant permissions
CREATE DATABASE nexus_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'nexus_ai'@'%' IDENTIFIED WITH mysql_native_password BY '<mysqlpwd>';
GRANT ALL PRIVILEGES ON nexus_ai.* TO 'nexus_ai'@'%';
FLUSH PRIVILEGES;
EXIT;

# Data import
mysql -u nexus_ai -p<mysqlpwd> nexus_ai < docker/mysql/db_init/nexus_ai.sql
```

Create and activate the basic conda environment. The default Python version we use is 3.10.13, We recommend using Python version >= 3.10 and <= 3.12 for compatibility.
```bash
cd NexusAI
conda create --name nexus_ai python=3.10.13 --no-default-packages
conda activate nexus_ai
conda env update -f conda/nexus_ai.yml
```

Copy `.env` and modify the `.env` configuration items as needed, For configuration instructions, refer to [docker-compose.yml configuration instructions](#docker-composeyml-configuration-instructions)
```bash
cp .env.template .env
```

Configure icon access rules through nginx
```nginx
server {
    listen 9475; # The port should be consistent with ICON_URL in .env

    location /tool_icon {
        alias NexusAI/assets/tool; # Fill in the real path of the project
        try_files $uri $uri/ =404;
    }
}
```

Restart nginx
```bash
systemctl restart nginx
```

Start the sandbox container
```bash
# The docker image tag should be consistent with the configuration in docker-compose.yml
docker pull edeai/sandbox:<tag>

# SANDBOX_PORT should be consistent with .env
# The mounted local storage directory should be changed to the real path
# SANDBOX_FASTAPI_WORKERS: The number of workers for the sandbox service
docker run -d --privileged -p <SANDBOX_PORT>:8001 -v NexusAI/storage:/storage -e SANDBOX_FASTAPI_WORKERS=2 edeai/sandbox:<tag>
```

Note that before executing all the Python scripts below, you must first execute `conda activate nexus_ai`

Start the API service
```bash
python app.py
```

Start Celery asynchronous task service
```bash
python celery_app.py
```

Start the websocket service
```bash
python websocket.py
```

Start meeting room service
```bash
python task/chatroom_run.py
```

Start the workflow service
```bash
python task/workflow_run.py
```

## WEB deployment
Go to the web directory and copy `envConfig.ts`, Modify the `envConfig.ts` configuration items as needed. For configuration instructions, refer to [docker-compose.yml configuration instructions](#docker-composeyml-configuration-instructions)
```bash
cd web
cp config/envConfig.ts.template config/envConfig.ts
```

Install dependency packages
```bash
npm install
```

Start the web service
```bash
# You can also use other instructions in package.json:scripts
npm run start
```

Visit NexusAI
```http
http://127.0.0.1:9471
```

When you visit for the first time, you can log in using the following initial administrator account
```
Email:
admin@nexusai.com

Password:
nexusaipwd
```

Note: To update the initial administrator password
```bash
python scripts/init_admin_password.py
```

## Pull NexusAI
1. Pull the updated content from the git repository
```bash
cd NexusAI
git pull origin main
```

2. If `conda/nexus_ai.yml` is updated, the conda environment needs to be updated
```bash
conda activate nexus_ai
conda env update -f conda/nexus_ai.yml
```

3. If there are `.sql` file updates in the `docker/multi_service/db_migrations directory`, you need to update the database
```bash
conda activate nexus_ai
python scripts/migrations.py
```

4. If the image corresponding to `docker-compose.yml:sandbox:image` is updated, you need to restart the sandbox container
```bash
# Find the running sandbox container
docker ps | grep sandbox

# Stop the container by the corresponding container id
docker stop <container_id>
# Delete the container by the corresponding container id
docker rm <container_id>
# Delete old images
docker rmi edeai/sandbox:<old tag>

# The docker image tag should be consistent with the configuration in docker-compose.yml
docker pull edeai/sandbox:<new tag>

# SANDBOX_PORT should be consistent with .env
# The mounted local storage directory should be changed to the real path
# SANDBOX_FASTAPI_WORKERS: The number of workers for the sandbox service
docker run -d --privileged -p <SANDBOX_PORT>:8001 -v NexusAI/storage:/storage -e SANDBOX_FASTAPI_WORKERS=2 edeai/sandbox:<new tag>
```

5. Note that the updated content in `.env.template` is synchronized to `.env`, and the updated content in `web/config/envConfig.ts.template` is synchronized to `web/config/envConfig.ts`

6. Restart each service in turn `API` `Celery` `websocket` `meeting room` `workflow` `web` 