"""
Step 4: Exporter - Create Excel and CSV tables for manual verification.
"""
import pandas as pd
from pathlib import Path
from typing import List
from loguru import logger

from .models import Place
from .config_loader import config_loader


# Column definitions for output table
OUTPUT_COLUMNS = [
    # Core info
    "name",
    "category",
    "city",
    "address",
    "phone",
    "opening_hours",

    # Contact details
    "mobile",
    "email",
    "contact_name",
    "operator",
    "brand",

    # Social / website
    "social_url",
    "website",
    "contact_website",
    "contact_facebook",
    "contact_instagram",
    "contact_telegram",
    "contact_whatsapp",

    # Classification & priority
    "group",
    "priority_score",
    "priority_level",

    # Verification link
    "google_maps_link",

    # Empty columns for manual verification
    "verified",
    "notes",
    "contact_person",
    "contact_phone",
    "contact_email",
    "status",

    # Metadata (hidden by default but available)
    "osm_id",
    "lat",
    "lon",
    "street",
    "housenumber",
    "suburb",
    "postcode",
    "cuisine",
    "wheelchair",
    "outdoor_seating",
    "takeaway",
    "delivery",
    "fetched_at"
]

COLUMN_LABELS = {
    "name": "Название",
    "category": "Категория",
    "city": "Город",
    "address": "Адрес",
    "phone": "Телефон",
    "opening_hours": "Часы работы",
    "mobile": "Мобильный",
    "email": "Email",
    "contact_name": "Контактное лицо",
    "operator": "Оператор",
    "brand": "Бренд",
    "social_url": "Соцсеть",
    "website": "Website",
    "contact_website": "Contact Website",
    "contact_facebook": "Facebook",
    "contact_instagram": "Instagram",
    "contact_telegram": "Telegram",
    "contact_whatsapp": "WhatsApp",
    "group": "Группа (A/B)",
    "priority_score": "Приоритет (баллы)",
    "priority_level": "Уровень приоритета",
    "google_maps_link": "Ссылка на Google Maps",
    "verified": "Проверено (да/нет)",
    "notes": "Примечания",
    "contact_person": "Контактное лицо (доп.)",
    "contact_phone": "Телефон (доп.)",
    "contact_email": "Email (доп.)",
    "status": "Статус",
}


def prepare_export_dataframe(places: List[Place]) -> pd.DataFrame:
    """Prepare DataFrame with selected columns and Russian labels."""
    rows = []
    for place in places:
        row = place.to_dict()

        # Add google maps link
        row["google_maps_link"] = place.get_google_maps_link()

        # Ensure all output columns exist
        for col in OUTPUT_COLUMNS:
            if col not in row:
                row[col] = ""

        rows.append(row)

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    return df


def export_to_excel(places: List[Place], output_path: Path) -> None:
    """Export places to Excel with formatting."""
    df = prepare_export_dataframe(places)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Places")

        # Get worksheet for formatting
        ws = writer.sheets["Places"]

        # Set column widths
        column_widths = {
            "A": 30,   # name
            "B": 15,   # category
            "C": 15,   # city
            "D": 40,   # address
            "E": 18,   # phone
            "F": 25,   # opening_hours
            "G": 18,   # mobile
            "H": 25,   # email
            "I": 20,   # contact_name
            "J": 20,   # operator
            "K": 15,   # brand
            "L": 35,   # social_url
            "M": 35,   # website
            "N": 35,   # contact_website
            "O": 35,   # contact_facebook
            "P": 35,   # contact_instagram
            "Q": 35,   # contact_telegram
            "R": 35,   # contact_whatsapp
            "S": 12,   # group
            "T": 15,   # priority_score
            "U": 15,   # priority_level
            "V": 40,   # google_maps_link
            "W": 12,   # verified
            "X": 30,   # notes
            "Y": 20,   # contact_person
            "Z": 18,   # contact_phone
            "AA": 25,  # contact_email
            "AB": 15,  # status
        }

        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        # Freeze first row
        ws.freeze_panes = "A2"

        # Auto-filter
        ws.auto_filter.ref = ws.dimensions

    logger.info(f"Exported {len(df)} places to Excel: {output_path}")


def export_to_csv(places: List[Place], output_path: Path) -> None:
    """Export places to CSV."""
    df = prepare_export_dataframe(places)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"Exported {len(df)} places to CSV: {output_path}")


def export_summary(places: List[Place], output_path: Path) -> None:
    """Export summary statistics."""
    df = pd.DataFrame([p.to_dict() for p in places])

    summary = {
        "total": len(places),
        "by_group": df["group"].value_counts().to_dict() if "group" in df.columns else {},
        "by_category": df["category"].value_counts().to_dict() if "category" in df.columns else {},
        "by_city": df["city"].value_counts().head(20).to_dict() if "city" in df.columns else {},
        "by_priority_level": df["priority_level"].value_counts().to_dict() if "priority_level" in df.columns else {},
        "avg_priority_score": df["priority_score"].mean() if "priority_score" in df.columns else 0,
        "with_phone": df["phone"].astype(bool).sum() if "phone" in df.columns else 0,
        "with_email": df["email"].astype(bool).sum() if "email" in df.columns else 0,
        "with_social": df["social_url"].astype(bool).sum() if "social_url" in df.columns else 0,
        "with_opening_hours": df["opening_hours"].astype(bool).sum() if "opening_hours" in df.columns else 0,
    }

    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.info(f"Summary saved to: {output_path}")


def export_all(places: List[Place], output_dir: Path) -> None:
    """Export to all formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Main exports
    export_to_excel(places, output_dir / "places_for_verification.xlsx")
    export_to_csv(places, output_dir / "places_for_verification.csv")

    # Summary
    export_summary(places, output_dir / "export_summary.json")

    # Split by group for convenience
    for group in ["A", "B"]:
        group_places = [p for p in places if p.group == group]
        if group_places:
            export_to_excel(group_places, output_dir / f"places_group_{group}.xlsx")
            export_to_csv(group_places, output_dir / f"places_group_{group}.csv")

    # Split by priority level
    for level in ["high", "medium", "low"]:
        level_places = [p for p in places if p.priority_level == level]
        if level_places:
            export_to_excel(level_places, output_dir / f"places_priority_{level}.xlsx")

    logger.info(f"=== Step 4 Export Complete ===")
    logger.info(f"All files saved to: {output_dir}")


def main():
    """CLI entry point for export."""
    import sys
    import pandas as pd
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Load step 3 output
    input_path = Path("data/processed/step3_scored.parquet")
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

    # Export
    export_all(places, Path("data/output"))


if __name__ == "__main__":
    main()