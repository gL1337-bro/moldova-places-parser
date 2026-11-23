"""
Flask API server for PyWebView frontend.
"""
import os
import sys
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
from loguru import logger

# Add parser to path
sys.path.insert(0, str(Path(__file__).parent))

from parser import (
    PlaceExtractor, classify_places, score_places, export_all,
    config_loader, Place
)


app = Flask(__name__)
CORS(app)

# Global state
pipeline_state = {
    "status": "idle",  # idle, running, completed, error
    "current_step": 0,
    "total_steps": 4,
    "progress": 0,
    "message": "",
    "places_count": 0,
    "groups": {"A": 0, "B": 0, "C": 0},
    "priority_distribution": {"high": 0, "medium": 0, "low": 0},
    "error": None,
    "places": []
}

pipeline_thread = None


def run_pipeline_background():
    """Run the full pipeline in background thread."""
    global pipeline_state, pipeline_thread

    try:
        pipeline_state["status"] = "running"
        pipeline_state["current_step"] = 1
        pipeline_state["progress"] = 10
        pipeline_state["message"] = "Step 1: Extracting from Overpass API..."

        # Step 1: Extraction
        extractor = PlaceExtractor()
        places = extractor.run()
        pipeline_state["places_count"] = len(places)

        # Save step 1
        import pandas as pd
        df = pd.DataFrame([p.to_dict() for p in places])
        df.to_parquet("data/processed/step1_raw_places.parquet", index=False)

        # Step 2: Classification
        pipeline_state["current_step"] = 2
        pipeline_state["progress"] = 40
        pipeline_state["message"] = "Step 2: Classifying websites..."

        groups = classify_places(places)
        pipeline_state["groups"] = {k: len(v) for k, v in groups.items()}

        # Save step 2
        for group_name in ["A", "B"]:
            group_places = groups[group_name]
            if group_places:
                df = pd.DataFrame([p.to_dict() for p in group_places])
                df.to_parquet(f"data/processed/step2_group_{group_name}.parquet", index=False)

        combined = groups["A"] + groups["B"]

        # Step 3: Scoring
        pipeline_state["current_step"] = 3
        pipeline_state["progress"] = 70
        pipeline_state["message"] = "Step 3: Calculating priorities..."

        scored = score_places(combined)
        pipeline_state["priority_distribution"] = {
            "high": sum(1 for p in scored if p.priority_level == "high"),
            "medium": sum(1 for p in scored if p.priority_level == "medium"),
            "low": sum(1 for p in scored if p.priority_level == "low"),
        }

        # Save step 3
        df = pd.DataFrame([p.to_dict() for p in scored])
        df.to_parquet("data/processed/step3_scored.parquet", index=False)

        # Step 4: Export
        pipeline_state["current_step"] = 4
        pipeline_state["progress"] = 90
        pipeline_state["message"] = "Step 4: Exporting to Excel/CSV..."

        export_all(scored, Path("data/output"))

        # Complete
        pipeline_state["status"] = "completed"
        pipeline_state["progress"] = 100
        pipeline_state["message"] = "Pipeline completed successfully!"
        pipeline_state["places"] = [p.to_dict() for p in scored[:100]]  # First 100 for preview

    except Exception as e:
        logger.exception("Pipeline error")
        pipeline_state["status"] = "error"
        pipeline_state["error"] = str(e)
        pipeline_state["message"] = f"Error: {e}"


@app.route("/api/status")
def get_status():
    """Get pipeline status."""
    return jsonify(pipeline_state)


@app.route("/api/start", methods=["POST"])
def start_pipeline():
    """Start the pipeline."""
    global pipeline_thread

    if pipeline_state["status"] == "running":
        return jsonify({"error": "Pipeline already running"}), 400

    # Reset state
    pipeline_state.update({
        "status": "idle",
        "current_step": 0,
        "progress": 0,
        "message": "",
        "places_count": 0,
        "groups": {"A": 0, "B": 0, "C": 0},
        "priority_distribution": {"high": 0, "medium": 0, "low": 0},
        "error": None,
        "places": []
    })

    pipeline_thread = threading.Thread(target=run_pipeline_background, daemon=True)
    pipeline_thread.start()

    return jsonify({"status": "started"})


@app.route("/api/places")
def get_places():
    """Get places with pagination and filtering."""
    group = request.args.get("group", "all")
    priority = request.args.get("priority", "all")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search", "").lower()

    # Load latest data
    try:
        df = pd.read_parquet("data/processed/step3_scored.parquet")
    except FileNotFoundError:
        return jsonify({"places": [], "total": 0, "page": page, "per_page": per_page})

    # Filter
    if group != "all":
        df = df[df["group"] == group]
    if priority != "all":
        df = df[df["priority_level"] == priority]
    if search:
        mask = df["name"].str.lower().str.contains(search, na=False)
        mask |= df["city"].str.lower().str.contains(search, na=False)
        mask |= df["address"].str.lower().str.contains(search, na=False)
        df = df[mask]

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    df_page = df.iloc[start:end]

    places = df_page.to_dict(orient="records")
    return jsonify({
        "places": places,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    })


@app.route("/api/stats")
def get_stats():
    """Get summary statistics."""
    try:
        df = pd.read_parquet("data/processed/step3_scored.parquet")
    except FileNotFoundError:
        return jsonify({})

    stats = {
        "total": len(df),
        "by_group": df["group"].value_counts().to_dict() if "group" in df.columns else {},
        "by_category": df["category"].value_counts().to_dict() if "category" in df.columns else {},
        "by_city": df["city"].value_counts().head(20).to_dict() if "city" in df.columns else {},
        "by_priority_level": df["priority_level"].value_counts().to_dict() if "priority_level" in df.columns else {},
        "avg_priority_score": round(df["priority_score"].mean(), 1) if "priority_score" in df.columns else 0,
        "with_phone": int(df["phone"].astype(bool).sum()) if "phone" in df.columns else 0,
        "with_email": int(df["email"].astype(bool).sum()) if "email" in df.columns else 0,
        "with_social": int(df["social_url"].astype(bool).sum()) if "social_url" in df.columns else 0,
        "with_opening_hours": int(df["opening_hours"].astype(bool).sum()) if "opening_hours" in df.columns else 0,
    }
    return jsonify(stats)


@app.route("/api/export")
def export_data():
    """Download export files."""
    format = request.args.get("format", "excel")
    group = request.args.get("group", "all")

    try:
        df = pd.read_parquet("data/processed/step3_scored.parquet")
    except FileNotFoundError:
        return jsonify({"error": "No data available"}), 404

    if group != "all":
        df = df[df["group"] == group]

    from parser.exporter import prepare_export_dataframe
    from parser.models import Place

    places = [Place(**row.to_dict()) for _, row in df.iterrows()]
    export_df = prepare_export_dataframe(places)

    if format == "excel":
        output_path = "data/output/temp_export.xlsx"
        export_df.to_excel(output_path, index=False)
        return send_file(output_path, as_attachment=True, download_name=f"places_{group}.xlsx")
    else:
        output_path = "data/output/temp_export.csv"
        export_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return send_file(output_path, as_attachment=True, download_name=f"places_{group}.csv")


@app.route("/api/config")
def get_config():
    """Get current configuration."""
    return jsonify({
        "categories": config_loader.get_category_tags(),
        "category_labels": config_loader.get_category_labels(),
        "scoring_weights": config_loader.load_scoring_weights().weights,
        "social_domains": config_loader.load_social_domains().social_domains,
        "regions": config_loader.get_regions_for_query()
    })


@app.route("/api/config", methods=["POST"])
def update_config():
    """Update configuration (weights, social domains, etc.)."""
    data = request.get_json()
    # In a real app, you'd save to YAML files
    return jsonify({"status": "ok", "message": "Config update not implemented yet"})


def run_api(host="127.0.0.1", port=5000):
    """Run the Flask API server."""
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run_api()