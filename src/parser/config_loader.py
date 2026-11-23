"""
Configuration loader for YAML config files.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CategoryConfig:
    key: str
    tags: List[str]
    label: str


@dataclass
class RegionsConfig:
    municipalities: List[Dict[str, Any]]
    districts: List[Dict[str, Any]]
    excluded_bbox: Dict[str, float]
    excluded_cities: List[str]
    dubossary_left_bank_villages: List[str]


@dataclass
class SocialDomainsConfig:
    social_domains: List[str]
    social_patterns: List[str]


@dataclass
class ScoringWeightsConfig:
    weights: Dict[str, Any]
    thresholds: Dict[str, int]
    city_tiers: Dict[str, List[str]]
    category_bonus: Dict[str, int]


class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._categories: Optional[Dict[str, Any]] = None
        self._regions: Optional[RegionsConfig] = None
        self._social_domains: Optional[SocialDomainsConfig] = None
        self._scoring_weights: Optional[ScoringWeightsConfig] = None

    def load_categories(self) -> Dict[str, Any]:
        """Load categories configuration."""
        if self._categories is None:
            path = self.config_dir / "categories.yaml"
            with open(path, "r", encoding="utf-8") as f:
                self._categories = yaml.safe_load(f)
        return self._categories

    def load_regions(self) -> RegionsConfig:
        """Load regions configuration."""
        if self._regions is None:
            path = self.config_dir / "excluded_regions.yaml"
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._regions = RegionsConfig(**data)
        return self._regions

    def load_social_domains(self) -> SocialDomainsConfig:
        """Load social domains configuration."""
        if self._social_domains is None:
            path = self.config_dir / "social_domains.yaml"
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._social_domains = SocialDomainsConfig(**data)
        return self._social_domains

    def load_scoring_weights(self) -> ScoringWeightsConfig:
        """Load scoring weights configuration."""
        if self._scoring_weights is None:
            path = self.config_dir / "scoring_weights.yaml"
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._scoring_weights = ScoringWeightsConfig(**data)
        return self._scoring_weights

    def get_category_tags(self) -> Dict[str, List[str]]:
        """Get mapping of category key -> list of OSM tags."""
        cats = self.load_categories()
        return {key: val["tags"] for key, val in cats.items()}

    def get_category_labels(self) -> Dict[str, str]:
        """Get mapping of category key -> display label."""
        cats = self.load_categories()
        return {key: val["label"] for key, val in cats.items()}

    def get_excluded_tourism_tags(self) -> List[str]:
        """Get list of tourism tags to exclude."""
        cats = self.load_categories()
        return cats.get("excluded_tourism", [])

    def get_all_fields(self) -> List[str]:
        """Get list of all fields to extract from OSM."""
        cats = self.load_categories()
        fields = cats.get("fields", {})
        all_fields = []
        for field_list in fields.values():
            all_fields.extend(field_list)
        return all_fields

    def get_regions_for_query(self) -> List[Dict[str, Any]]:
        """Get all regions (municipalities + districts) for querying."""
        regions = self.load_regions()
        all_regions = []

        for m in regions.municipalities:
            all_regions.append({
                "name": m["name"],
                "bbox": m["bbox"],
                "type": "municipality",
                "city_filter": m.get("city_filter", [])
            })

        for d in regions.districts:
            all_regions.append({
                "name": d["name"],
                "bbox": d["bbox"],
                "type": "district",
                "city_filter": []
            })

        return all_regions

    def is_excluded_city(self, city_name: str) -> bool:
        """Check if city is in excluded list (case-insensitive)."""
        regions = self.load_regions()
        city_lower = city_name.lower().strip()
        for excluded in regions.excluded_cities:
            if excluded.lower() in city_lower:
                return True
        for village in regions.dubossary_left_bank_villages:
            if village.lower() in city_lower:
                return True
        return False

    def is_in_excluded_bbox(self, lon: float, lat: float) -> bool:
        """Check if coordinates fall in excluded bbox (Transnistria)."""
        regions = self.load_regions()
        bbox = regions.excluded_bbox
        return (bbox["min_lon"] <= lon <= bbox["max_lon"] and
                bbox["min_lat"] <= lat <= bbox["max_lat"])

    def get_city_tier(self, city_name: str) -> str:
        """Get city tier: large, medium, small, or village."""
        weights = self.load_scoring_weights()
        city_lower = city_name.lower().strip()

        for tier, cities in weights.city_tiers.items():
            for c in cities:
                if c.lower() in city_lower:
                    return tier

        return "village"

    def get_category_bonus(self, category: str) -> int:
        """Get bonus score for category."""
        weights = self.load_scoring_weights()
        return weights.category_bonus.get(category, 0)


# Global config loader instance
config_loader = ConfigLoader()


if __name__ == "__main__":
    loader = ConfigLoader()
    print("Categories:", loader.get_category_tags())
    print("Regions count:", len(loader.get_regions_for_query()))
    print("Excluded cities:", loader.load_regions().excluded_cities[:5])