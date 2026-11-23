"""
Step 3: Scorer - Calculate priority scores for places.
"""
from typing import List, Dict, Any
from loguru import logger

from .config_loader import config_loader
from .models import Place


class PriorityScorer:
    def __init__(self):
        self.weights_config = config_loader.load_scoring_weights()
        self.weights = self.weights_config.weights
        self.thresholds = self.weights_config.thresholds

    def score_place(self, place: Place) -> float:
        """Calculate priority score for a single place."""
        score = 0.0

        # Contact info
        if place.get_primary_phone():
            score += self.weights.get("has_phone", 15)
        if place.mobile:
            score += self.weights.get("has_mobile", 10)
        if place.email:
            score += self.weights.get("has_email", 12)
        if place.get_primary_website():
            score += self.weights.get("has_website_field", 5)

        # Opening hours
        if place.opening_hours:
            score += self.weights.get("has_opening_hours", 10)

        # Social media
        social_count = len(place.get_social_urls())
        if social_count > 0:
            score += self.weights.get("has_social", 8)
        if social_count >= 2:
            score += self.weights.get("has_multiple_social", 5)

        # City tier
        city_tier = config_loader.get_city_tier(place.city)
        if city_tier == "large":
            score += self.weights.get("large_city", 10)
        elif city_tier == "medium":
            score += self.weights.get("medium_city", 6)
        elif city_tier == "small":
            score += self.weights.get("small_city", 3)
        else:
            score += self.weights.get("village", 1)

        # Address completeness
        if place.street and place.housenumber:
            score += self.weights.get("has_full_address", 8)
        elif place.street:
            score += self.weights.get("has_street_only", 4)
        elif place.city:
            score += self.weights.get("has_city_only", 2)

        # Data quality
        if place.name:
            score += self.weights.get("has_name", 5)
            # Bonus for name length (up to +5)
            name_bonus = min(len(place.name) * self.weights.get("name_length_bonus", 0.1), 5)
            score += name_bonus

        if place.brand:
            score += self.weights.get("has_brand", 3)
        if place.operator:
            score += self.weights.get("has_operator", 3)
        if place.cuisine:
            score += self.weights.get("has_cuisine", 2)

        # Category bonus
        cat_bonus = config_loader.get_category_bonus(place.category)
        score += cat_bonus

        return round(score, 1)

    def get_priority_level(self, score: float) -> str:
        """Convert score to priority level."""
        if score >= self.thresholds.get("high_priority", 50):
            return "high"
        elif score >= self.thresholds.get("medium_priority", 30):
            return "medium"
        else:
            return "low"

    def score_places(self, places: List[Place]) -> List[Place]:
        """Score all places and assign priority levels."""
        logger.info("=== Step 3: Scoring Places ===")

        scored = []
        level_counts = {"high": 0, "medium": 0, "low": 0}

        for place in places:
            score = self.score_place(place)
            place.priority_score = score
            place.priority_level = self.get_priority_level(score)
            level_counts[place.priority_level] += 1
            scored.append(place)

        # Sort by priority score descending
        scored.sort(key=lambda p: p.priority_score, reverse=True)

        logger.info(f"Priority distribution: {level_counts}")
        logger.info(f"Top score: {scored[0].priority_score if scored else 0}")
        logger.info(f"Avg score: {sum(p.priority_score for p in scored) / len(scored) if scored else 0:.1f}")

        return scored


def score_places(places: List[Place]) -> List[Place]:
    """Convenience function to score places."""
    scorer = PriorityScorer()
    return scorer.score_places(places)


def main():
    """CLI entry point for scoring."""
    import sys
    import pandas as pd
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Load step 2 output
    input_path = Path("data/processed/step2_groups_ab.parquet")
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

    # Score
    scored = score_places(places)

    # Save
    out_df = pd.DataFrame([p.to_dict() for p in scored])
    out_path = Path("data/processed/step3_scored.parquet")
    out_df.to_parquet(out_path, index=False)
    print(f"Saved {len(scored)} scored places to {out_path}")


if __name__ == "__main__":
    main()