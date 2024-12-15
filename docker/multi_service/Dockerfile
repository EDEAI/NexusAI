FROM continuumio/anaconda3:2024.02-1

# Use network proxy as needed
ARG HTTP_PROXY=http://192.168.0.187:10809
ARG HTTPS_PROXY=http://192.168.0.187:10809

COPY conda/nexus_ai.yml /tmp/nexus_ai.yml
RUN conda env create -f /tmp/nexus_ai.yml --verbose && conda clean -afy && rm -rf /tmp/*
RUN echo "conda activate nexus_ai" >> ~/.bashrc
ENV PATH /opt/conda/envs/nexus_ai/bin:/opt/conda/bin:$PATH

RUN conda install -c conda-forge supervisor

COPY api /NexusAI/api
COPY core /NexusAI/core
COPY docker/multi_service/db_migrations /NexusAI/docker/multi_service/db_migrations
COPY docker/multi_service/init_admin_password.py /NexusAI/docker/multi_service/init_admin_password.py
COPY docker/multi_service/migrations.py /NexusAI/docker/multi_service/migrations.py
COPY docker/multi_service/import_documents_to_vdb.py /NexusAI/docker/multi_service/import_documents_to_vdb.py
COPY docker/multi_service/supervisord.conf /etc/supervisord.conf
COPY task /NexusAI/task
COPY .env.template /NexusAI/.env
COPY app.py /NexusAI/app.py
COPY celery_app.py /NexusAI/celery_app.py
COPY config.py /NexusAI/config.py
COPY languages.py /NexusAI/languages.py
COPY log.py /NexusAI/log.py
COPY websocket.py /NexusAI/websocket.py

WORKDIR /NexusAI

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
