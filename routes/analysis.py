import pandas as pd
from flask import Blueprint, jsonify
from sqlalchemy import text

from db import engine
from utils import error
from flask import Blueprint, jsonify, request

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


def calculate_consumption(rows):
    """Turn a meter's readings into consumption per period.

    A period runs from one reading to the next. If the value drops,
    the pair is a meter reset: it is marked 'reset' and not counted.
    """
    if len(rows) < 2:
        return []

    df = pd.DataFrame([dict(r) for r in rows])
    df["cumulative_kwh"] = df["cumulative_kwh"].astype(float)
    df["period_start"] = df["reading_date"].shift(1)
    df["consumption_kwh"] = df["cumulative_kwh"].diff()
    df = df.dropna(subset=["period_start"])

    periods = []
    for r in df.itertuples():
        is_reset = r.consumption_kwh < 0
        periods.append({
            "period_start": r.period_start.isoformat(),
            "period_end": r.reading_date.isoformat(),
            "consumption_kwh": None if is_reset else round(r.consumption_kwh, 2),
            "status": "reset" if is_reset else "valid",
        })
    return periods


@analysis_bp.get("/consumption/<int:meter_id>")
def meter_consumption(meter_id):
    with engine.connect() as conn:
        meter = conn.execute(
            text("SELECT 1 FROM meters WHERE meter_id = :m"), {"m": meter_id}
        ).first()
        if meter is None:
            return error("meter not found", 404)

        rows = conn.execute(
            text("SELECT reading_date, cumulative_kwh FROM meter_readings "
                 "WHERE meter_id = :m ORDER BY reading_date"),
            {"m": meter_id},
        ).mappings().all()

    return jsonify(meter_id=meter_id, periods=calculate_consumption(rows))
def summarize(periods, level):
    """Group consumption periods by month ('2026-01') or year ('2026')."""
    if not periods:
        return []

    df = pd.DataFrame(periods)
    cut = 7 if level == "monthly" else 4
    df["label"] = df["period_start"].str[:cut]

    valid = df[df["status"] == "valid"]
    totals = valid.groupby("label")["consumption_kwh"].agg(["sum", "count"])
    resets = df[df["status"] == "reset"].groupby("label").size()

    result = []
    for label in sorted(df["label"].unique()):
        has_valid = label in totals.index
        result.append({
            "period": label,
            "total_kwh": round(float(totals.loc[label, "sum"]), 2) if has_valid else 0.0,
            "valid_periods": int(totals.loc[label, "count"]) if has_valid else 0,
            "reset_periods": int(resets.get(label, 0)),
        })
    return result


@analysis_bp.get("/summary/<int:meter_id>")
def meter_summary(meter_id):
    level = request.args.get("level", "monthly")
    if level not in ("monthly", "yearly"):
        return error("level must be 'monthly' or 'yearly'", 400)

    with engine.connect() as conn:
        meter = conn.execute(
            text("SELECT 1 FROM meters WHERE meter_id = :m"), {"m": meter_id}
        ).first()
        if meter is None:
            return error("meter not found", 404)

        rows = conn.execute(
            text("SELECT reading_date, cumulative_kwh FROM meter_readings "
                 "WHERE meter_id = :m ORDER BY reading_date"),
            {"m": meter_id},
        ).mappings().all()

    periods = calculate_consumption(rows)
    return jsonify(meter_id=meter_id, level=level, summary=summarize(periods, level))
