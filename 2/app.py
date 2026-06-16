"""
Backend server. Serves the search page and a JSON search API backed by
the SQLite database built by ingest_csv_to_db.py.

Run with:
    python app.py

Then open http://localhost:5000 in a browser.
"""

import sqlite3
import json
from flask import Flask, request, jsonify, send_from_directory

DB_PATH = "companies.db"
META_PATH = "db_meta.json"

app = Flask(__name__, static_folder="static")

with open(META_PATH) as f:
    META = json.load(f)

TABLE = META["table"]
COLUMNS = META["columns"]
NAME_COL = META["name_column"]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/meta")
def meta():
    conn = get_conn()
    count = conn.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    conn.close()
    return jsonify({
        "columns": COLUMNS,
        "name_column": NAME_COL,
        "total_rows": count,
    })


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": [], "count": 0})

    conn = get_conn()
    like_term = f"%{q}%"
    query = (
        f'SELECT * FROM {TABLE} '
        f'WHERE "{NAME_COL}" LIKE ? COLLATE NOCASE '
        f'ORDER BY "{NAME_COL}" LIMIT 50'
    )
    rows = conn.execute(query, (like_term,)).fetchall()
    conn.close()

    results = [dict(row) for row in rows]
    return jsonify({"results": results, "count": len(results)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
