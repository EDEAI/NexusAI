from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field


class VersionInfo(BaseModel):
    version: str
    description: Optional[str] = None
    dependencies: Optional[Dict[str, str]] = None
    devDependencies: Optional[Dict[str, str]] = None
    main: Optional[str] = None
    scripts: Optional[Dict[str, str]] = None
    author: Optional[Any] = None
    license: Optional[str] = None
    repository: Optional[Any] = None
    homepage: Optional[str] = None
    keywords: Optional[List[str]] = None


class PackageMaintainer(BaseModel):
    name: str
    email: Optional[str] = None


class PackageInfo(BaseModel):
    name: str
    description: Optional[str] = None
    dist_tags: Dict[str, str] = Field(alias="dist-tags")
    versions: Dict[str, VersionInfo]
    time: Optional[Dict[str, str]] = None
    author: Optional[Any] = None
    repository: Optional[Any] = None
    readme: Optional[str] = None
    maintainers: Optional[List[PackageMaintainer]] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    keywords: Optional[List[str]] = None


class SearchResult(BaseModel):
    package: Dict[str, Any]
    score: Dict[str, Any]
    searchScore: float

    @property
    def name(self) -> str:
        return self.package.get("name", "")

    @property
    def version(self) -> str:
        return self.package.get("version", "")

    @property
    def description(self) -> Optional[str]:
        return self.package.get("description")


class SearchResponse(BaseModel):
    objects: List[SearchResult]
    total: int
    time: str


class NpmRegistryClient:
    def __init__(
        self, base_url: str = "https://registry.npmjs.org", timeout: float = 30.0
    ):
        self.base_url = base_url
        self.client = httpx.Client(timeout=timeout)

    def get_package_info(self, package_name: str) -> PackageInfo:
        """Retrieve detailed information about an npm package"""
        url = f"{self.base_url}/{quote(package_name)}"
        response = self.client.get(url)
        response.raise_for_status()
        return PackageInfo.model_validate(response.json())

    def get_package_version_info(self, package_name: str, version: str) -> VersionInfo:
        """Retrieve detailed information about a specific version of an npm package"""
        url = f"{self.base_url}/{quote(package_name)}/{version}"
        response = self.client.get(url)
        response.raise_for_status()
        return VersionInfo.model_validate(response.json())

    def search_packages(
        self,
        query: str,
        size: int = 20,
        popularity: float = 0.5,
        quality: float = 0.5,
        maintenance: float = 0.5,
    ) -> SearchResponse:
        """Search for npm packages

        Args:
            query: Search keyword
            size: Number of results to return
            popularity: Weight for popularity (0-1)
            quality: Weight for quality (0-1)
            maintenance: Weight for maintenance (0-1)
        """
        url = "https://registry.npmjs.org/-/v1/search"
        params = {
            "text": query,
            "size": size,
            "popularity": popularity,
            "quality": quality,
            "maintenance": maintenance,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return SearchResponse.model_validate(response.json())

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
