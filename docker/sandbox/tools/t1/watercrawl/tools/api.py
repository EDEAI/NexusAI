import json
from typing import Union, Generator
from urllib.parse import urljoin
import warnings

import requests
from requests import Response


class BaseAPIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.session = self.init_session()

    def init_session(self):
        session = requests.Session()
        session.headers.update({'X-API-Key': self.api_key})
        session.headers.update({'Content-Type': 'application/json'})
        session.headers.update({'Accept': 'application/json'})
        session.headers.update({'User-Agent': 'WaterCrawl-Plugin'})
        session.headers.update({'Accept-Language': 'en-US'})
        return session

    def _get(self, endpoint: str, query_params: dict = None, **kwargs):
        return self.session.get(
            urljoin(self.base_url, endpoint),
            params=query_params,
            **kwargs
        )

    def _post(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.post(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )

    def _put(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.put(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )

    def _delete(self, endpoint: str, query_params: dict = None, **kwargs):
        return self.session.delete(
            urljoin(self.base_url, endpoint),
            params=query_params,
            **kwargs
        )

    def _patch(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.patch(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )


class WaterCrawlAPIClient(BaseAPIClient):
    def __init__(self, api_key, base_url: str = 'https://app.watercrawl.dev/'):
        super().__init__(api_key, base_url)

    def process_eventstream(self, response: Response):
        for line in response.iter_lines():
            line = line.decode('utf-8')
            if line.startswith('data:'):
                line = line[5:].strip()
                data = json.loads(line)
                yield data

    def process_response(self, response: Response) -> Union[dict, bytes, list, None, Generator]:
        response.raise_for_status()
        if response.status_code == 204:
            return None
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()

        if response.headers.get('Content-Type') == 'application/octet-stream':
            return response.content

        if response.headers.get('Content-Type') == 'text/event-stream':
            return self.process_eventstream(response)

        if response.headers.get('Content-Type') == 'application/zip':
            return response.content

        raise Exception(f'Unknown response type: {response.headers.get("Content-Type")}')

    def get_crawl_requests_list(self, page: int = None, page_size: int = None):
        query_params = {
            'page': page or 1,
            'page_size': page_size or 10
        }
        return self.process_response(
            self._get(
                '/api/v1/core/crawl-requests/',
                query_params=query_params,
            )
        )

    def get_crawl_request(self, item_id: str):
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/',
            )
        )

    def create_crawl_request(
            self,
            url: Union[list, str] = None,
            spider_options: dict = None,
            page_options: dict = None,
            plugin_options: dict = None
    ):
        data = {
            # 'urls': url if isinstance(url, list) else [url],
            'url': url,
            'options': {
                'spider_options': spider_options or {},
                'page_options': page_options or {},
                'plugin_options': plugin_options or {},
            }
        }
        return self.process_response(
            self._post(
                '/api/v1/core/crawl-requests/',
                data=data,
            )
        )

    def stop_crawl_request(self, item_id: str):
        return self.process_response(
            self._delete(
                f'/api/v1/core/crawl-requests/{item_id}/',
            )
        )

    def download_crawl_request(self, item_id: str):
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/download/',
            )
        )

    def monitor_crawl_request(self, item_id: str, download=True) -> Generator:
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/status/',
                stream=True,
                query_params={
                    'prefetched': download
                }
            )
        )

    def get_crawl_request_results(self, item_id: str, page: int = None, page_size: int = None):
        query_params = {
            'page': page or 1,
            'page_size': page_size or 10
        }
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/results/',
                query_params=query_params,
            )
        )

    def scrape_url(self,
                   url: str,
                   page_options: dict = None,
                   plugin_options: dict = None,
                   sync: bool = True,
                   download: bool = True
                   ):
        result = self.create_crawl_request(
            url=url,
            page_options=page_options,
            plugin_options=plugin_options
        )
        if not sync:
            return result

        for result in self.monitor_crawl_request(result['uuid'], download):
            if result['type'] == 'result':
                return result['data']

    def download_result(self, result_object: dict):
        """[DEPRECATED] Download and parse the result object if necessary. Will be removed in a future version."""
        warnings.warn(
            "download_result is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        if isinstance(result_object['result'], dict):
            return result_object
        response = requests.get(result_object['result'])
        response.raise_for_status()
        result_object['result'] = response.json()
        return result_object

    def __get_crawl_request_for_sitemap(self, crawl_request: Union[str, dict]) -> dict:
        if isinstance(crawl_request, str):
            crawl_request = self.get_crawl_request(crawl_request)

        if 'sitemap' not in crawl_request:
            raise ValueError('Sitemap not found in crawl request')

        return crawl_request

    def download_sitemap(self, crawl_request: Union[str, dict]) -> dict:
        """
        Download the sitemap for a given crawl request.

        Args:
            crawl_request: Either a crawl request UUID string or a crawl request object

        Returns:
            The sitemap data as a dictionary or list

        Raises:
            ValueError: If the sitemap is not found in the crawl request
            HTTPError: If there's an error fetching the sitemap
        """
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)

        response = requests.get(crawl_request['sitemap'])
        response.raise_for_status()
        return response.json()

    def download_sitemap_graph(self, crawl_request: Union[str, dict]) -> bytes:
        """
        Download the sitemap as a graph representation for visualization.

        Args:
            crawl_request: Either a crawl request UUID string or a crawl request object

        Returns:
            The sitemap graph data

        Raises:
            ValueError: If the sitemap is not found in the crawl request
            HTTPError: If there's an error fetching the sitemap graph
        """
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)

        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{crawl_request["uuid"]}/sitemap/graph/',
            )
        )

    def download_sitemap_markdown(self, crawl_request: Union[str, dict]) -> bytes:
        """
        Download the sitemap as a markdown document.

        Args:
            crawl_request: Either a crawl request UUID string or a crawl request object

        Returns:
            The sitemap as markdown content

        Raises:
            ValueError: If the sitemap is not found in the crawl request
            HTTPError: If there's an error fetching the sitemap markdown
        """
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)

        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{crawl_request["uuid"]}/sitemap/markdown/',
            )
        )

    def get_search_requests_list(self, page: int = None, page_size: int = None) -> dict:
        """
        Get a paginated list of search requests.

        Args:
            page: Page number (1-indexed, default: 1)
            page_size: Number of items per page (default: 10)

        Returns:
            Dictionary containing paginated search requests
        """
        query_params = {
            'page': page or 1,
            'page_size': page_size or 10
        }
        return self.process_response(
            self._get(
                '/api/v1/core/search/',
                query_params=query_params,
            )
        )

    def get_search_request(self, item_id: str, download: bool = False) -> dict:
        """
        Get details of a specific search request.

        Args:
            item_id: UUID of the search request

        Returns:
            Dictionary containing search request details
        """
        return self.process_response(
            self._get(
                f'/api/v1/core/search/{item_id}/',
                query_params={
                    'prefetched': download
                }
            )
        )

    def create_search_request(self, query: str, search_options: dict = None, result_limit: int = 5, sync: bool = True,
                              download: bool = True) -> Union[dict, Generator]:
        """
        Create a new search request.

        Args:
            query: Search query string
            search_options: Dictionary of search options
                - language: Language code (e.g., "en", "fr")
                - country: Country code (e.g., "us", "fr")
                - time_range: Time range filter (e.g., "any", "hour", "day", "week", "month", "year")
                - search_type: Type of search (e.g., "web")
                - depth: Search depth (e.g., "basic", "advanced", "ultimate")
            result_limit: Maximum number of results to return
            sync: If True, wait for results; if False, return immediately
            download: If True, download results; if False, return URLs

        Returns:
            If sync=True: Complete search results
            If sync=False: Search request object with UUID for monitoring

        Raises:
            Exception: If the search request fails
        """
        response = self.process_response(
            self._post(
                '/api/v1/core/search/',
                data={
                    'query': query,
                    'search_options': search_options or {},
                    'result_limit': result_limit
                }
            )
        )

        if not sync:
            return response

        for result in self.monitor_search_request(response['uuid'], download):
            if result['type'] == 'state' and result['data']['status'] in ["finished", "failed"]:
                return result['data']

        raise Exception('Search request failed')

    def monitor_search_request(self, item_id: str, download=True) -> Generator:
        """
        Monitor a search request in real-time.

        Args:
            item_id: UUID of the search request to monitor
            download: If True, download results; if False, return URLs

        Returns:
            Generator yielding search events

        Yields:
            Dictionary containing event type and data
        """
        return self.process_response(
            self._get(
                f'/api/v1/core/search/{item_id}/status/',
                stream=True,
                query_params={
                    'prefetched': download
                }
            )
        )

    def stop_search_request(self, item_id: str) -> None:
        """
        Stop a running search request.

        Args:
            item_id: UUID of the search request to stop

        Returns:
            None
        """
        return self.process_response(
            self._delete(
                f'/api/v1/core/search/{item_id}/',
            )
        )
