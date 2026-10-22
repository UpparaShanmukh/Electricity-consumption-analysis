from flask import Flask, jsonify
from sqlalchemy import text

from db import engine

app = Flask(__name__)


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify(status="ok", database="connected")
    except Exception:
        return jsonify(error="database unreachable"), 503


@app.get("/consumers")
def list_consumers():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT consumer_id, consumer_code, consumer_type, region "
                 "FROM consumers ORDER BY consumer_id")
        ).mappings().all()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True)