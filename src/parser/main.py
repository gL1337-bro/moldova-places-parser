"""
Main orchestrator - runs all steps of the pipeline.
"""
import argparse
import sys
from pathlib import Path
from loguru import logger

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .extractor import PlaceExtractor
from .classifier import classify_places
from .scorer import score_places
from .exporter import export_all
from .models import Place


def run_step1() -> list:
    """Run Step 1: Extraction."""
    logger.info("=" * 50)
    logger.info("STEP 1: EXTRACTION FROM OVERPASS API")
    logger.info("=" * 50)

    extractor = PlaceExtractor()
    places = extractor.run()

    # Save intermediate
    import pandas as pd
    df = pd.DataFrame([p.to_dict() for p in places])
    output_path = Path("data/processed/step1_raw_places.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(places)} places to {output_path}")

    return places


def run_step2(places: list) -> dict:
    """Run Step 2: Classification."""
    logger.info("=" * 50)
    logger.info("STEP 2: CLASSIFICATION (A/B/C)")
    logger.info("=" * 50)

    groups = classify_places(places)

    # Save groups A and B
    import pandas as pd
    for group_name in ["A", "B"]:
        group_places = groups[group_name]
        if group_places:
            df = pd.DataFrame([p.to_dict() for p in group_places])
            out_path = Path(f"data/processed/step2_group_{group_name}.parquet")
            df.to_parquet(out_path, index=False)
            logger.info(f"Saved Group {group_name}: {len(group_places)} places")

    # Combined A+B for next step
    combined = groups["A"] + groups["B"]
    if combined:
        df = pd.DataFrame([p.to_dict() for p in combined])
        out_path = Path("data/processed/step2_groups_ab.parquet")
        df.to_parquet(out_path, index=False)
        logger.info(f"Saved combined A+B: {len(combined)} places")

    return groups


def run_step3(places: list) -> list:
    """Run Step 3: Scoring."""
    logger.info("=" * 50)
    logger.info("STEP 3: PRIORITY SCORING")
    logger.info("=" * 50)

    scored = score_places(places)

    # Save
    import pandas as pd
    df = pd.DataFrame([p.to_dict() for p in scored])
    out_path = Path("data/processed/step3_scored.parquet")
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(scored)} scored places to {out_path}")

    return scored


def run_step4(places: list) -> None:
    """Run Step 4: Export."""
    logger.info("=" * 50)
    logger.info("STEP 4: EXPORT TO EXCEL/CSV")
    logger.info("=" * 50)

    export_all(places, Path("data/output"))


def load_places_from_parquet(path: Path) -> list:
    """Load places from parquet file."""
    import pandas as pd
    df = pd.read_parquet(path)
    places = []
    for _, row in df.iterrows():
        place = Place(**row.to_dict())
        places.append(place)
    return places


def main():
    parser = argparse.ArgumentParser(description="Moldova Places Parser")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 0],
                        help="Run specific step (0 = all steps)")
    parser.add_argument("--resume", type=str,
                        help="Resume from parquet file")

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("data/processed/pipeline.log", level="DEBUG", rotation="10 MB")

    if args.step == 1 or args.step == 0:
        places = run_step1()
        if args.step != 0:
            return

    if args.step == 2 or args.step == 0:
        if args.resume:
            places = load_places_from_parquet(Path(args.resume))
        elif 'places' not in locals():
            places = load_places_from_parquet(Path("data/processed/step1_raw_places.parquet"))
        groups = run_step2(places)
        if args.step != 0:
            return
        places = groups["A"] + groups["B"]

    if args.step == 3 or args.step == 0:
        if args.resume:
            places = load_places_from_parquet(Path(args.resume))
        elif 'places' not in locals():
            places = load_places_from_parquet(Path("data/processed/step2_groups_ab.parquet"))
        places = run_step3(places)
        if args.step != 0:
            return

    if args.step == 4 or args.step == 0:
        if args.resume:
            places = load_places_from_parquet(Path(args.resume))
        elif 'places' not in locals():
            places = load_places_from_parquet(Path("data/processed/step3_scored.parquet"))
        run_step4(places)

    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()