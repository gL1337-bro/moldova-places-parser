"""
Overpass API client with rate limiting, retries, and response caching.
"""
import os
import time
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger


@dataclass
class OverpassConfig:
    base_url: str = "https://overpass-api.de/api/interpreter"
    timeout: int = 180
    max_retries: int = 3
    min_request_interval: float = 2.0  # seconds between requests
    cache_dir: str = "data/raw"


class OverpassClient:
    def __init__(self, config: Optional[OverpassConfig] = None):
        self.config = config or OverpassConfig()
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MoldovaPlacesParser/1.0 (contact: your-email@example.com)"
        })

    def _get_cache_path(self, query: str) -> Path:
        """Generate cache file path from query hash."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return self.cache_dir / f"overpass_{query_hash}.json"

    def _load_from_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Load response from cache if exists."""
        cache_path = self._get_cache_path(query)
        if cache_path.exists():
            logger.info(f"Loading from cache: {cache_path.name}")
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _save_to_cache(self, query: str, data: Dict[str, Any]) -> None:
        """Save response to cache."""
        cache_path = self._get_cache_path(query)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Saved to cache: {cache_path.name}")

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.min_request_interval:
            sleep_time = self.config.min_request_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True
    )
    def _make_request(self, query: str) -> Dict[str, Any]:
        """Make HTTP request to Overpass API with retries."""
        self._rate_limit()

        logger.debug(f"Sending query to Overpass API (len={len(query)})")
        response = self.session.post(
            self.config.base_url,
            data={"data": query},
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute Overpass query with caching.
        
        Args:
            query: Overpass QL query string
            use_cache: Whether to use cached response if available
            
        Returns:
            Parsed JSON response from Overpass API
        """
        if use_cache:
            cached = self._load_from_cache(query)
            if cached is not None:
                return cached

        data = self._make_request(query)

        if use_cache:
            self._save_to_cache(query, data)

        return data

    def query_bbox(self, bbox: List[float], tags: List[str],
                   element_types: List[str] = None) -> Dict[str, Any]:
        """
        Query objects in bounding box with given tags.
        
        Args:
            bbox: [min_lon, min_lat, max_lon, max_lat]
            tags: List of tag filters like ["amenity=cafe", "shop=bakery"]
            element_types: ["node", "way", "relation"] (default: all)
            
        Returns:
            Overpass API response
        """
        if element_types is None:
            element_types = ["node", "way", "relation"]

        min_lon, min_lat, max_lon, max_lat = bbox

        tag_filters = " ".join([f'["{tag}"]' for tag in tags])
        elements = " ".join(element_types)

        query = f"""
        [out:json][timeout:{self.config.timeout}];
        (
          {elements}{tag_filters}({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out body;
        >;
        out skel qt;
        """

        return self.query(query.strip())

    def query_area(self, area_name: str, tags: List[str],
                   element_types: List[str] = None) -> Dict[str, Any]:
        """Query objects in a named area (e.g., country, region)."""
        if element_types is None:
            element_types = ["node", "way", "relation"]

        tag_filters = " ".join([f'["{tag}"]' for tag in tags])
        elements = " ".join(element_types)

        query = f"""
        [out:json][timeout:{self.config.timeout}];
        area["name"="{area_name}"]->.searchArea;
        (
          {elements}{tag_filters}(area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """

        return self.query(query.strip())


def build_category_query(bbox: List[float], category_tags: List[str],
                         excluded_tags: List[str] = None,
                         fields: List[str] = None) -> str:
    """
    Build optimized Overpass QL query for a category in a bbox.
    
    Args:
        bbox: [min_lon, min_lat, max_lon, max_lat]
        category_tags: List of tags to include (e.g., ["amenity=cafe"])
        excluded_tags: List of tags to exclude (e.g., ["tourism=hotel"])
        fields: Additional fields to include in output
        
    Returns:
        Overpass QL query string
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    include_filters = " ".join([f'["{tag}"]' for tag in category_tags])
    exclude_filters = ""
    if excluded_tags:
        exclude_filters = " ".join([f'["{tag}"!~".*"]' for tag in excluded_tags])

    extra_fields = ""
    if fields:
        extra_fields = "\n  ".join([f'out:{field};' for field in fields])

    query = f"""
    [out:json][timeout:180];
    (
      node{include_filters}{exclude_filters}({min_lat},{min_lon},{max_lat},{max_lon});
      way{include_filters}{exclude_filters}({min_lat},{min_lon},{max_lat},{max_lon});
      relation{include_filters}{exclude_filters}({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out body;
    >;
    out skel qt;
    """

    return query.strip()


if __name__ == "__main__":
    # Test client
    client = OverpassConfig(cache_dir="data/raw")
    print("OverpassClient config:", client)