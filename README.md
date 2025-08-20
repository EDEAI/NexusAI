[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/edeai-nexusai-badge.png)](https://mseep.ai/app/edeai-nexusai)

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

## Initialize model, storage, and logs directories
```bash
cd NexusAI
mkdir -p models storage logs upload_files
chmod 777 storage logs upload_files
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

Copy `docker-compose.yml` and modify the `docker-compose.yml` configuration items as needed. For configuration instructions, refer to [docker-compose.yml configuration instructions](#docker-composeyml-configuration-instructions)
```bash
cp docker-compose.yml.template docker-compose.yml
```

Start all Docker containers
```bash
docker-compose up -d
```

After running the command, you should see output similar to the following, showing the status of all containers
```bash
[+] Running 15/15
 ✔ Network nexusai_my_network                  Created                          0.1s
 ✔ Volume "nexusai_mysql_data"                 Created                          0.0s
 ✔ Volume "nexusai_minio_data"                 Created                          0.0s
 ✔ Volume "nexusai_milvus_data"                Created                          0.0s
 ✔ Volume "nexusai_etcd_data"                  Created                          0.0s
 ✔ Volume "nexusai_redis_data"                 Created                          0.0s
 ✔ Container nexusai-docker-sandbox            Started                          2.6s
 ✔ Container nexusai-docker-milvus-etcd        Started                          2.6s
 ✔ Container nexusai-docker-nginx              Started                          2.6s
 ✔ Container nexusai-docker-milvus-minio       Started                          2.6s
 ✔ Container nexusai-docker-redis              Started                          2.6s
 ✔ Container nexusai-docker-web                Started                          2.6s
 ✔ Container nexusai-docker-mariadb            Started                          2.5s
 ✔ Container nexusai-docker-milvus-standalone  Started                          2.4s
 ✔ Container nexusai-docker-multi-service      Started                          5.5s
```

Finally, you can check whether all containers are running normally
```bash
docker-compose ps
```

In the output below, you can see three business service containers `nexusai-docker-multi-service` `nexusai-docker-web`, and the rest are basic service containers
```bash
NAME                               IMAGE                                      COMMAND                   SERVICE             CREATED          STATUS                    PORTS
nexusai-docker-mariadb             mariadb:11.4                               "docker-entrypoint.s…"   mariadb             50 minutes ago   Up 50 minutes             0.0.0.0:9461->3306/tcp
nexusai-docker-milvus-etcd         quay.io/coreos/etcd:v3.5.5                 "etcd -advertise-cli…"   etcd                50 minutes ago   Up 50 minutes (healthy)   2379-2380/tcp
nexusai-docker-milvus-minio        minio/minio:RELEASE.2023-03-20T20-16-18Z   "/usr/bin/docker-ent…"   minio               50 minutes ago   Up 50 minutes (healthy)   9000/tcp
nexusai-docker-milvus-standalone   milvusdb/milvus:v2.3.1                     "/tini -- milvus run…"   milvus-standalone   50 minutes ago   Up 50 minutes (healthy)   0.0.0.0:9463->19530/tcp
nexusai-docker-multi-service       edeai/multi_service:0.0.3                  "supervisord -c /etc…"   multi_service       50 minutes ago   Up 50 minutes
nexusai-docker-nginx               nginx:latest                               "/docker-entrypoint.…"   nginx               50 minutes ago   Up 40 minutes             0.0.0.0:9470->80/tcp
nexusai-docker-redis               redis:6.2                                  "docker-entrypoint.s…"   redis               50 minutes ago   Up 50 minutes             0.0.0.0:9462->6379/tcp
nexusai-docker-sandbox             edeai/sandbox:0.0.4                        "python api_server.py"   sandbox             50 minutes ago   Up 50 minutes             0.0.0.0:9464->8001/tcp
nexusai-docker-web                 edeai/web:0.0.2                            "docker-entrypoint.s…"   web                 50 minutes ago   Up 50 minutes
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

Note that the initial administrator password can be changed through the web interface after first login

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
# Make sure to synchronize the updated content in `docker-compose.yml.template` to `docker-compose.yml`
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
# Database related configuration
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

# API, websocket and roundtable websocket service port configuration
API_PORT: 9472
WEBSOCKET_PORT: 9473
CHATROOM_WEBSOCKET_PORT: 9474

# Web access address
WEB_URL: http://127.0.0.1:9470

# Backend icon resource access address
ICON_URL: http://127.0.0.1:9470

# Backend storage resource access address
STORAGE_URL: http://127.0.0.1:9470

# Agent/workflow API access timeout
APP_API_TIMEOUT: 60

# Number of api service workers
FASTAPI_WORKERS: 2

# Number of celery service workers
CELERY_WORKERS: 4

# SMTP email configuration
SMTP_SERVER: 
SMTP_PORT: 587
SMTP_USERNAME: 
SMTP_PASSWORD: 
SMTP_USE_TLS: true
SMTP_TIMEOUT: 30
```

Front-end environment variables
```yaml
# Backend API service access address
WEB_API_URL: http://127.0.0.1:9470
# Backend websocket service address (except roundtable service)
WEB_WS_URL: ws://127.0.0.1:9470/ws
# Backend roundtable service websocket service address
WEB_CHAT_URL: ws://127.0.0.1:9470/ws_chat
```

# Source code deployment

## Prerequisites
Before deploying NexusAI locally, we need to deploy the following basic services:
1. [Docker](https://docs.docker.com/engine/install/)
2. [nginx](https://nginx.org/en/docs/install.html)
3. [MariaDB](https://mariadb.org/download/)
4. [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
5. [Milvus](https://milvus.io/docs/install_standalone-docker-compose.md)
6. [Anaconda](https://docs.anaconda.com/anaconda/install/)
7. [Node.js (>=20.0)](https://nodejs.org/en/download/package-manager)

[Clone the NexusAI source code to your local environment](#clone-nexusai)

## Milvus Authentication
If you want to enable Milvus authentication, refer to [Milvus Authentication](https://milvus.io/docs/authenticate.md) to set up Milvus authentication.

## Server deployment
[Initialize model, storage, and logs directories](#initialize-model-storage-and-logs-directories)

[Cloning the Embedding and Reranker models for offline mode](#cloning-the-embedding-and-reranker-models-for-offline-mode)

Initialize the database
```bash
cd NexusAI

# Login to mariadb
mariadb -u root -p

# Create a database, user, and grant permissions
CREATE DATABASE nexus_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'nexus_ai'@'%' IDENTIFIED BY '<mysqlpwd>';
GRANT ALL PRIVILEGES ON nexus_ai.* TO 'nexus_ai'@'%';
FLUSH PRIVILEGES;
EXIT;

# Data import
mariadb -u nexus_ai -p<mysqlpwd> nexus_ai < docker/mysql/db_init/nexus_ai.sql
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

Configure icon and storage access rules through nginx
```nginx
server {
    listen 9475; # The port should be consistent with ICON_URL in `.env`

    location /tool_icon {
        alias NexusAI/assets/tool; # Fill in the real path of the project

        if ($request_filename ~ "/$|/[^\.]+$") {
            return 403;
        }

        try_files $uri =404;
    }

    location /head_icon {
        alias NexusAI/assets/head; # Fill in the real path of the project

        if ($request_filename ~ "/$|/[^\.]+$") {
            return 403;
        }

        try_files $uri =404;
    }
}

server {
    listen 9476; # The port should be consistent with STORAGE_URL in `.env`

    location /file {
        alias NexusAI/storage; # Fill in the real path of the project

        if ($request_filename ~ "/$|/[^\.]+$") {
            return 403;
        }

        add_header Content-Disposition "attachment";

        try_files $uri =404;
    }

    location /upload {
        alias NexusAI/upload_files; # Fill in the real path of the project

        if ($request_filename ~ "/$|/[^\.]+$") {
            return 403;
        }

        add_header Content-Disposition "attachment";

        try_files $uri =404;
    }
}
```

Restart nginx
```bash
systemctl restart nginx
```

Start the sandbox container
```bash
# The docker image tag should be consistent with the configuration in `docker-compose.yml`
docker pull edeai/sandbox:<tag>

# SANDBOX_PORT should be consistent with `.env`
# The mounted local directory should be changed to the real path
# SANDBOX_FASTAPI_WORKERS: The number of workers for the sandbox service
docker run -d --privileged -p <SANDBOX_PORT>:8001 -v NexusAI/storage:/storage -v NexusAI/upload_files:/upload_files -v NexusAI/docker/volumes/venv_cache:/app/venv_cache -v NexusAI/docker/sandbox/tools:/app/tools:ro -v NexusAI/docker/volumes/logs/sandbox:/app/logs -e SANDBOX_FASTAPI_WORKERS=2 edeai/sandbox:<tag>
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

## Launch NexusAI
Go to the project root directory, and copy `supervisord.conf`. Modify the configurations in `supervisord.conf` as needed.
```bash
cp supervisord.conf.template supervisord.conf
```

Activate the conda environment and start all services using supervisord
```bash
conda activate nexus_ai
supervisord -c supervisord.conf
```

Check the status of all services
```bash
supervisorctl -c supervisord.conf status
```

You should see output similar to the following, showing the status of all services
```bash
ai_tool                          RUNNING   pid 121123, uptime 0:00:11
api                              RUNNING   pid 121124, uptime 0:00:11
celery                           RUNNING   pid 121125, uptime 0:00:11
import_documents_to_vdb          RUNNING   pid 121126, uptime 0:00:11
migrations                       FATAL     Exited too quickly (process log may have details)
roundtable                       RUNNING   pid 121128, uptime 0:00:11
web                              RUNNING   pid 121129, uptime 0:00:11
websocket                        RUNNING   pid 121130, uptime 0:00:11
workflow                         RUNNING   pid 121131, uptime 0:00:11
```

Visit NexusAI
```http
http://localhost:9471
```

When you visit for the first time, you can log in using the following initial administrator account
```
Email:
admin@nexusai.com

Password:
nexusaipwd
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

3. If the image corresponding to `docker-compose.yml:sandbox:image` is updated, you need to restart the sandbox container
```bash
# Find the running sandbox container
docker ps | grep sandbox

# Stop the container by the corresponding container id
docker stop <container_id>
# Delete the container by the corresponding container id
docker rm <container_id>
# Delete old images
docker rmi edeai/sandbox:<old tag>

# The docker image tag should be consistent with the configuration in `docker-compose.yml`
docker pull edeai/sandbox:<new tag>

# SANDBOX_PORT should be consistent with `.env`
# The mounted local directory should be changed to the real path
# SANDBOX_FASTAPI_WORKERS: The number of workers for the sandbox service
docker run -d --privileged -p <SANDBOX_PORT>:8001 -v NexusAI/storage:/storage -v NexusAI/upload_files:/upload_files -v NexusAI/docker/volumes/venv_cache:/app/venv_cache -v NexusAI/docker/sandbox/tools:/app/tools:ro -v NexusAI/docker/volumes/logs/sandbox:/app/logs -e SANDBOX_FASTAPI_WORKERS=2 edeai/sandbox:<new tag>
```

4. Note that the updated content in `.env.template` is synchronized to `.env`, and the updated content in `web/config/envConfig.ts.template` is synchronized to `web/config/envConfig.ts`

5. Restart all services
```bash
conda activate nexus_ai
supervisorctl -c supervisord.conf restart all
```