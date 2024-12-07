FROM ubuntu:22.04

# Use network proxy as needed
# ARG HTTP_PROXY=http://192.168.0.241:10809
# ARG HTTPS_PROXY=http://192.168.0.241:10809

RUN apt-get clean && apt-get update && apt-get install -y firejail

COPY conda/Anaconda3-2023.03-0-Linux-x86_64.sh /tmp/anaconda.sh
COPY conda/nexus_ai.yml /tmp/nexus_ai.yml

RUN bash /tmp/anaconda.sh -b -p /opt/conda && rm /tmp/anaconda.sh

ENV PATH /opt/conda/bin:$PATH

RUN conda env create -f /tmp/nexus_ai.yml --verbose

RUN echo "source activate nexus_ai" > ~/.bashrc

ENV PATH /opt/conda/envs/nexus_ai/bin:$PATH

CMD ["/bin/bash"]