FROM python:3.10.13

# Use network proxy as needed
# ARG HTTP_PROXY=http://192.168.1.5:10809
# ARG HTTPS_PROXY=http://192.168.1.5:10809

RUN apt-get update && apt-get install -y firejail

RUN pip install --no-cache-dir fastapi uvicorn jinja2

WORKDIR /docker/sandbox

COPY ./api_server.py /docker/sandbox

CMD ["python", "api_server.py"]