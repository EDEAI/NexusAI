import pika
import os

def get_rabbit_client(data: dict[str]):
    addresses = data.get('addresses')
    host = str(addresses).split(':')[0]
    port = str(addresses).split(':')[1]
    username = data.get('username')
    password = data.get('password')
    vhost = data.get('vhost')
    return pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.PlainCredentials(
            username=username,
            password=password
        ),
        virtual_host=vhost,
        heartbeat=6000  # 增加心跳检测
    )