"""
Main entry point for PyWebView desktop application.
"""
import os
import sys
import threading
import time
import webview
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from api import app as flask_app


def start_flask():
    """Start Flask server in background thread."""
    flask_app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)


class Api:
    """JavaScript API bridge for PyWebView."""

    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def get_status(self):
        """Get pipeline status."""
        import requests
        try:
            resp = requests.get("http://127.0.0.1:5000/api/status", timeout=2)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_pipeline(self):
        """Start the pipeline."""
        import requests
        try:
            resp = requests.post("http://127.0.0.1:5000/api/start", timeout=5)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_places(self, group="all", priority="all", page=1, per_page=50, search=""):
        """Get places with filters."""
        import requests
        try:
            params = {
                "group": group,
                "priority": priority,
                "page": page,
                "per_page": per_page,
                "search": search
            }
            resp = requests.get("http://127.0.0.1:5000/api/places", params=params, timeout=5)
            return resp.json()
        except Exception as e:
            return {"places": [], "total": 0, "error": str(e)}

    def get_stats(self):
        """Get statistics."""
        import requests
        try:
            resp = requests.get("http://127.0.0.1:5000/api/stats", timeout=5)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def export_data(self, format="excel", group="all"):
        """Trigger export download."""
        import requests
        try:
            params = {"format": format, "group": group}
            resp = requests.get("http://127.0.0.1:5000/api/export", params=params, timeout=30)
            # In PyWebView, we'd handle file download differently
            return {"status": "ok", "message": "Export triggered"}
        except Exception as e:
            return {"error": str(e)}

    def open_external(self, url):
        """Open URL in default browser."""
        import webbrowser
        webbrowser.open(url)
        return {"status": "ok"}


def main():
    """Main entry point."""
    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Wait for Flask to start
    time.sleep(2)

    # Create API bridge
    api = Api()

    # Create webview window
    ui_path = Path(__file__).parent / "ui" / "dist" / "index.html"

    if ui_path.exists():
        # Production: load built React app
        window = webview.create_window(
            "Moldova Places Parser",
            str(ui_path),
            js_api=api,
            width=1400,
            height=900,
            min_size=(1000, 700),
            text_select=True
        )
    else:
        # Development: load from Vite dev server
        window = webview.create_window(
            "Moldova Places Parser",
            "http://localhost:5173",
            js_api=api,
            width=1400,
            height=900,
            min_size=(1000, 700),
            text_select=True
        )

    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()