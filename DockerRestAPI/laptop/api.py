"""RESTful service exposing stored brevet control open and close times."""
import csv
from datetime import datetime
import io
import os
from flask import Flask, request, Response
from flask_restful import Resource, Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient(os.environ.get('DB_PORT_27017_TCP_ADDR', 'db'), 27017)
db = client.tododb


def parse_brevet_time(time_str):
    """Parse 'Thu 1/1 2:37' style strings into a datetime for chronological sorting."""
    try:
        parts = time_str.split(" ", 1)
        return datetime.strptime(parts[1], "%m/%d %H:%M")
    except Exception:
        return datetime.max


def get_controls(mode="all", top=None):
    """Fetch stored controls from MongoDB, filtered by mode and optional top-k."""
    items = list(db.tododb.find({}, {"_id": 0}))
    records = []

    for item in items:
        entry = {}
        if mode in ("all", "open") and item.get("open"):
            entry["open"] = item["open"]
        if mode in ("all", "close") and item.get("close"):
            entry["close"] = item["close"]
        if entry:
            records.append(entry)

    # Sort chronologically in ascending order
    sort_key = "close" if mode == "close" else "open"
    records.sort(key=lambda r: parse_brevet_time(r.get(sort_key, "")))

    if top is not None and top > 0:
        records = records[:top]

    return records


def parse_top():
    """Parse optional ?top=k query parameter; returns None if absent or invalid."""
    raw = request.args.get("top")
    if raw is None:
        return None
    try:
        val = int(raw)
        return val if val > 0 else None
    except ValueError:
        return None


def to_csv_response(rows, fieldnames):
    """Serialize a list of dicts into a CSV HTTP response."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return Response(buf.getvalue(), mimetype="text/csv")


class ListAll(Resource):
    """Returns all open and close times (JSON default, or CSV)."""
    def get(self, fmt="json"):
        rows = get_controls(mode="all", top=parse_top())
        if fmt == "csv":
            return to_csv_response(rows, ["open", "close"])
        return {"controls": rows}


class ListOpenOnly(Resource):
    """Returns open times only (JSON default, or CSV)."""
    def get(self, fmt="json"):
        rows = get_controls(mode="open", top=parse_top())
        if fmt == "csv":
            return to_csv_response(rows, ["open"])
        return {"controls": rows}


class ListCloseOnly(Resource):
    """Returns close times only (JSON default, or CSV)."""
    def get(self, fmt="json"):
        rows = get_controls(mode="close", top=parse_top())
        if fmt == "csv":
            return to_csv_response(rows, ["close"])
        return {"controls": rows}


api.add_resource(ListAll, "/listAll", "/listAll/<string:fmt>")
api.add_resource(ListOpenOnly, "/listOpenOnly", "/listOpenOnly/<string:fmt>")
api.add_resource(ListCloseOnly, "/listCloseOnly", "/listCloseOnly/<string:fmt>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)