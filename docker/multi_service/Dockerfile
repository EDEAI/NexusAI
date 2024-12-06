FROM docker.io/edeai/nexusai_python_base:0.0.2

WORKDIR /NexusAI

COPY . /NexusAI

CMD ["sh", "-c", "python docker/multi_service/init_admin_password.py & python docker/multi_service/migrations.py & python app.py & python websocket.py & python task/chatroom_run.py & python task/workflow_run.py"]
