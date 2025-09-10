import abc
import logging
import random
import urllib.parse
from typing import List, Tuple

from kazoo.client import KazooClient
from kazoo.retry import KazooRetry

import nacos

class RegistryStrategy(abc.ABC):
    """Registry strategy abstract class"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def get_provider(self, address: str, interface: str) -> str:
        """
        Get service provider URI from registry
        
        Parameters:
            address: registry address
            interface: interface name
            
        Returns:
            provider URI, format: protocol://host:port
        """
        pass
        
    def select_provider_by_weight(self, weighted_hosts: List[Tuple[str, float]]) -> str:
        """
        Select service provider based on weight
        
        Parameters:
            weighted_hosts: service provider list, each element is a tuple of (uri, weight)
            
        Returns:
            selected service provider URI
        """
        self.logger.debug(f"Registry: select provider by weight: {weighted_hosts}")
        if not weighted_hosts:
            raise ValueError("No available service provider")
            
        total_weight = sum(weight for _, weight in weighted_hosts)
        
        if total_weight <= 0:
            return random.choice([uri for uri, _ in weighted_hosts])
            
        hit = random.random() * total_weight
        self.logger.debug(f"Registry: Random number: {hit}, total weight: {total_weight}")
        current_weight = 0
        for uri, weight in weighted_hosts:
            current_weight += weight
            if hit < current_weight:
                return uri
                
        return random.choice([uri for uri, _ in weighted_hosts])


class ZookeeperRegistryStrategy(RegistryStrategy):
    """ZooKeeper registry strategy implementation"""

    def __init__(self):
        super().__init__()
        self.DUBBO_ZK_PROVIDERS = '/dubbo/{}/providers'

    def get_provider(self, address: str, interface: str) -> str:
        """
        Get provider URI from ZooKeeper
        
        Parameters:
            address: ZooKeeper address, format: host:port
            interface: interface name
            
        Returns:
            Provider URI, format: protocol://host:port
        """
        import time
        start_time = time.time()
        
        self.logger.debug(f"ZooKeeper: get provider: {address}, {interface}")
        
        connection_retry = KazooRetry(max_tries=3, delay=1.0, backoff=1.5)
        zk = KazooClient(
            hosts=address,
            connection_retry=connection_retry
        )
        
        try:
            self.logger.debug("ZooKeeper: start connection...")
            zk.start(timeout=10)
            self.logger.debug("ZooKeeper: connection success")
            
            providers_path = self.DUBBO_ZK_PROVIDERS.format(interface)
            
            self.logger.debug(f"ZooKeeper: get providers path: {providers_path}")
            
            if not zk.exists(providers_path):
                self.logger.error(f"ZooKeeper: service: {interface} not exists")
                raise ValueError(f"ZooKeeper: service: {interface} not found")
            
            providers = zk.get_children(providers_path)
            self.logger.debug(f"ZooKeeper: get providers: {len(providers)}")
            self.logger.debug(f"ZooKeeper: providers: {providers}")
            
            # Support providers with multiple protocols
            protocol_providers = []
            for provider in providers:
                decoded_provider = urllib.parse.unquote(provider)
                self.logger.debug(f"ZooKeeper: decoded provider: {decoded_provider}")
                
                # Check if it's a valid URI (with protocol prefix)
                if '://' in decoded_provider:
                    protocol_providers.append(provider)
            
            self.logger.info(f"ZooKeeper: service: {interface} get providers: {protocol_providers}")
            if not protocol_providers:
                raise ValueError(f"ZooKeeper: service: {interface} has no available providers")
                
            weighted_hosts = []
            for provider in protocol_providers:
                provider_url = urllib.parse.unquote(provider)
                try:
                    url_result = urllib.parse.urlparse(provider_url)
                    # Extract protocol and host:port
                    protocol = url_result.scheme
                    host = url_result.netloc
                    
                    # Complete URI
                    uri = f"{protocol}://{host}"
                    
                    query_params = dict(urllib.parse.parse_qsl(url_result.query))
                    weight = float(query_params.get('weight', 100))
                    weighted_hosts.append((uri, weight))
                    self.logger.debug(f"Provider {uri} weight: {weight}")
                except Exception as e:
                    self.logger.warning(f"Parse provider URL failed: {provider_url}, {str(e)}")
            
            if not weighted_hosts:
                self.logger.error(f"ZooKeeper: no valid provider found: {protocol_providers}")
                raise ValueError(f"Cannot parse valid URI from provider URL")
                
            return self.select_provider_by_weight(weighted_hosts)
        finally:
            elapsed_time = time.time() - start_time
            self.logger.debug(f"ZooKeeper: get provider cost: {elapsed_time:.2f} seconds")
            try:
                self.logger.debug("ZooKeeper: close connection...")
                zk.stop()
                zk.close()
                self.logger.debug("ZooKeeper: connection closed")
            except Exception as e:
                self.logger.error(f"ZooKeeper: close connection failed: {str(e)}")


class NacosRegistryStrategy(RegistryStrategy):
    """Nacos registry strategy implementation"""

    def get_provider(self, address: str, interface: str) -> str:
        """
        Get provider URI from Nacos
        
        Parameters:
            address: Nacos address, format: host:port
            interface: interface name
            
        Returns:
            Provider URI, format: protocol://host:port
        """
        
        self.logger.debug(f"Nacos: get provider: {address}, {interface}")
        
        try:
            if ":" in address:
                host, port = address.split(":")
                port = int(port)
            else:
                host = address
                port = 8848 
                
            try:
                self.logger.debug("Nacos: try to connect to Nacos server...")
                
                nacos_client = nacos.NacosClient(address)
                
                instances = nacos_client.list_naming_instance(service_name=f"providers:{interface}::")
                self.logger.debug(f"Nacos: get instances: {instances}")
                if instances and 'hosts' in instances and instances['hosts']:
                    weighted_hosts = []
                    for instance in instances['hosts']:
                        host_ip = instance.get('ip')
                        host_port = instance.get('port')
                        weight = float(instance.get('weight', 1.0))
                        
                        # Get protocol, default is dubbo
                        metadata = instance.get('metadata', {})
                        protocol = metadata.get('protocol', 'dubbo')
                        
                        if host_ip and host_port:
                            uri = f"{protocol}://{host_ip}:{host_port}"
                            weighted_hosts.append((uri, weight))
                    
                    if weighted_hosts:
                        return self.select_provider_by_weight(weighted_hosts)
                    else:
                        self.logger.error(f"Nacos: no valid provider found for service: {interface}")
                        raise ValueError(f"Nacos: service {interface} has no valid providers")
                else:
                    self.logger.error(f"Nacos: service {interface} not found or has no instances")
                    raise ValueError(f"Nacos: service {interface} not found in registry")
            except Exception as e:
                self.logger.warning(f"Nacos: service query failed: {str(e)}")
                # Re-raise exception instead of ignoring
                raise e
        except Exception as e:
            self.logger.error(f"Nacos: get provider failed: {str(e)}", exc_info=True)
            raise e


class RegistryFactory:
    """Registry factory, responsible for creating the corresponding registry strategy instance"""

    @staticmethod
    def create_registry(registry_type: str) -> RegistryStrategy:
        """
        Create registry strategy instance
        
        Parameters:
            registry_type: registry type, such as 'zookeeper', 'nacos'
            
        Returns:
            Registry strategy instance
        """
        if registry_type == "zookeeper":
            # TODO: Temporarily not supporting zk, async threads in dify plugin environment cannot get provider
            raise ValueError(f"Registry: unsupported type: {registry_type}") 
            # return ZookeeperRegistryStrategy()
        elif registry_type == "nacos":
            return NacosRegistryStrategy()
        else:
            raise ValueError(f"Registry: unsupported type: {registry_type}") 