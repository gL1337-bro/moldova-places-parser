"""
Step 1: Extractor - Download places from Overpass API by regions.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from loguru import logger

from .overpass_client import OverpassClient, OverpassConfig, build_category_query
from .config_loader import config_loader
from .models import Place, parse_osm_element, ExtractionStats


class PlaceExtractor:
    def __init__(self, client: Optional[OverpassClient] = None,
                 output_dir: str = "data/processed"):
        self.client = client or OverpassClient()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = ExtractionStats()
        self.categories = config_loader.get_category_tags()
        self.category_labels = config_loader.get_category_labels()
        self.excluded_tourism = config_loader.get_excluded_tourism_tags()

    def extract_region(self, region: Dict[str, Any]) -> List[Place]:
        """Extract all places for a single region."""
        region_name = region["name"]
        bbox = region["bbox"]
        region_type = region["type"]

        logger.info(f"Extracting {region_name} ({region_type})...")
        all_places = []

        for cat_key, tags in self.categories.items():
            cat_label = self.category_labels.get(cat_key, cat_key)
            logger.debug(f"  Category: {cat_label}")

            query = build_category_query(
                bbox=bbox,
                category_tags=tags,
                excluded_tags=self.excluded_tourism
            )

            try:
                response = self.client.query(query)
                elements = response.get("elements", [])

                for elem in elements:
                    place = parse_osm_element(elem, cat_key, cat_label)
                    if place:
                        # Check if in excluded area (Transnistria)
                        if config_loader.is_in_excluded_bbox(place.lon, place.lat):
                            self.stats.excluded_transnistria += 1
                            continue
                        if config_loader.is_excluded_city(place.city):
                            self.stats.excluded_transnistria += 1
                            continue

                        all_places.append(place)
                        self.stats.add_category(cat_key)
                        self.stats.add_city(place.city or "Unknown")

                self.stats.total_fetched += len([p for p in all_places if p.category == cat_key])

            except Exception as e:
                error_msg = f"Error extracting {cat_key} in {region_name}: {e}"
                logger.error(error_msg)
                self.stats.errors.append(error_msg)

        logger.info(f"  Found {len(all_places)} places in {region_name}")
        return all_places

    def extract_all(self, regions: Optional[List[Dict[str, Any]]] = None) -> List[Place]:
        """Extract places from all regions."""
        if regions is None:
            regions = config_loader.get_regions_for_query()

        logger.info(f"Starting extraction from {len(regions)} regions...")
        all_places = []

        for region in tqdm(regions, desc="Regions"):
            places = self.extract_region(region)
            all_places.extend(places)

            # Small pause between regions
            time.sleep(0.5)

        logger.info(f"Total raw places: {len(all_places)}")
        return all_places

    def deduplicate(self, places: List[Place]) -> List[Place]:
        """Remove duplicates based on name + coordinates proximity."""
        logger.info("Deduplicating...")
        seen = {}
        unique = []

        for place in places:
            # Key: normalized name + rounded coordinates (100m precision)
            name_key = place.name.lower().strip()
            coord_key = (round(place.lat, 4), round(place.lon, 4))
            key = (name_key, coord_key)

            if key not in seen:
                seen[key] = place
                unique.append(place)
            else:
                self.stats.duplicates_removed += 1
                # Keep the one with more data
                existing = seen[key]
                if (place.phone or place.email or place.website) and \
                   not (existing.phone or existing.email or existing.website):
                    seen[key] = place
                    unique[-1] = place

        logger.info(f"Removed {self.stats.duplicates_removed} duplicates")
        return unique

    def remove_nameless(self, places: List[Place]) -> List[Place]:
        """Remove places without names."""
        original = len(places)
        filtered = [p for p in places if p.name and p.name.strip()]
        self.stats.no_name_removed = original - len(filtered)
        logger.info(f"Removed {self.stats.no_name_removed} places without names")
        return filtered

    def save_raw_responses(self, region: Dict[str, Any], responses: Dict[str, Any]) -> None:
        """Save raw Overpass responses for a region."""
        region_name = region["name"].replace(" ", "_").replace("/", "_")
        filepath = self.output_dir / f"raw_{region_name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

    def run(self, regions: Optional[List[Dict[str, Any]]] = None) -> List[Place]:
        """Run full extraction pipeline."""
        logger.info("=== Step 1: Extraction Started ===")

        # Extract all
        raw_places = self.extract_all(regions)

        # Deduplicate
        places = self.deduplicate(raw_places)

        # Remove nameless
        places = self.remove_nameless(places)

        # Save stats
        stats_path = self.output_dir / "extraction_stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(self.stats.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info(f"=== Step 1 Complete: {len(places)} places ===")
        logger.info(f"By category: {self.stats.by_category}")
        logger.info(f"Top cities: {dict(sorted(self.stats.by_city.items(), key=lambda x: -x[1])[:10])}")

        return places


def main():
    """CLI entry point for extraction."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    extractor = PlaceExtractor()
    places = extractor.run()

    # Save intermediate result
    import pandas as pd
    df = pd.DataFrame([p.to_dict() for p in places])
    output_path = Path("data/processed") / "step1_raw_places.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Saved {len(places)} places to {output_path}")


if __name__ == "__main__":
    main()