"""
Step 2: Classifier - Determine website status groups (A, B, C).
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from loguru import logger

from .config_loader import config_loader
from .models import Place


class WebsiteClassifier:
    def __init__(self):
        self.social_config = config_loader.load_social_domains()
        self.social_domains = set(d.lower() for d in self.social_config.social_domains)
        self.social_patterns = [re.compile(p, re.IGNORECASE) for p in self.social_config.social_patterns]

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            domain = parsed.netloc.lower().replace("www.", "")
            return domain
        except Exception:
            return ""

    def is_social_domain(self, url: str) -> bool:
        """Check if URL belongs to social media / aggregator / free builder domain."""
        if not url:
            return False

        domain = self.extract_domain(url)
        if not domain:
            return False

        # Exact domain match
        if domain in self.social_domains:
            return True

        # Subdomain match (e.g., something.facebook.com)
        for social in self.social_domains:
            if domain.endswith("." + social) or domain == social:
                return True

        # Pattern match
        for pattern in self.social_patterns:
            if pattern.search(url):
                return True

        return False

    def get_social_url(self, place: Place) -> str:
        """Extract the primary social media URL from a place."""
        # Priority order for social URLs
        social_fields = [
            "contact_instagram",
            "contact_facebook",
            "contact_twitter",
            "contact_linkedin",
            "contact_youtube",
            "contact_whatsapp",
            "contact_telegram",
            "contact_skype",
            "website",
            "contact_website"
        ]

        for field in social_fields:
            url = getattr(place, field, "")
            if url and self.is_social_domain(url):
                return url

        return ""

    def classify(self, place: Place) -> Tuple[str, str]:
        """
        Classify place into group A, B, or C.
        
        Returns:
            (group, social_url) where group is 'A', 'B', or 'C'
        """
        website = place.website or ""
        contact_website = place.contact_website or ""

        # Check both fields
        has_website = bool(website.strip())
        has_contact_website = bool(contact_website.strip())

        # Group C: Has own domain website (not social/aggregator/free)
        if has_website and not self.is_social_domain(website):
            return "C", ""
        if has_contact_website and not self.is_social_domain(contact_website):
            return "C", ""

        # Group B: Website field contains only social/aggregator/free domain
        if has_website and self.is_social_domain(website):
            social_url = self.get_social_url(place) or website
            return "B", social_url
        if has_contact_website and self.is_social_domain(contact_website):
            social_url = self.get_social_url(place) or contact_website
            return "B", social_url

        # Group A: No website at all
        return "A", ""


def classify_places(places: List[Place]) -> Dict[str, List[Place]]:
    """
    Classify all places into groups A, B, C.
    
    Returns:
        Dict with keys 'A', 'B', 'C' containing lists of places
    """
    classifier = WebsiteClassifier()
    groups = {"A": [], "B": [], "C": []}
    group_b_examples = []

    for place in places:
        group, social_url = classifier.classify(place)
        place.group = group
        place.social_url = social_url
        groups[group].append(place)

        if group == "B" and len(group_b_examples) < 10:
            group_b_examples.append({
                "name": place.name,
                "category": place.category,
                "city": place.city,
                "website": place.website,
                "contact_website": place.contact_website,
                "social_url": social_url
            })

    logger.info(f"=== Step 2 Classification Complete ===")
    logger.info(f"Group A (no website): {len(groups['A'])}")
    logger.info(f"Group B (social/aggregator only): {len(groups['B'])}")
    logger.info(f"Group C (own website): {len(groups['C'])}")

    if group_b_examples:
        logger.info("Group B examples:")
        for ex in group_b_examples:
            logger.info(f"  {ex['name']} ({ex['category']}, {ex['city']}) -> {ex['social_url']}")

    return groups


def main():
    """CLI entry point for classification."""
    import sys
    import pandas as pd
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Load step 1 output
    input_path = Path("data/processed/step1_raw_places.parquet")
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    df = pd.read_parquet(input_path)
    print(f"Loaded {len(df)} places")

    # Convert to Place objects
    from .models import Place
    places = []
    for _, row in df.iterrows():
        place = Place(**row.to_dict())
        places.append(place)

    # Classify
    groups = classify_places(places)

    # Save groups A and B (C is discarded)
    for group_name in ["A", "B"]:
        group_places = groups[group_name]
        if group_places:
            out_df = pd.DataFrame([p.to_dict() for p in group_places])
            out_path = Path(f"data/processed/step2_group_{group_name}.parquet")
            out_df.to_parquet(out_path, index=False)
            print(f"Saved Group {group_name}: {len(group_places)} places to {out_path}")

    # Save combined A+B for next step
    combined = groups["A"] + groups["B"]
    if combined:
        out_df = pd.DataFrame([p.to_dict() for p in combined])
        out_path = Path("data/processed/step2_groups_ab.parquet")
        out_df.to_parquet(out_path, index=False)
        print(f"Saved combined A+B: {len(combined)} places to {out_path}")


if __name__ == "__main__":
    main()