import os
from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
import acp_times

app = Flask(__name__)
app.secret_key = "brevet"

client = MongoClient(os.environ.get('DB_PORT_27017_TCP_ADDR', 'db'), 27017)
db = client.tododb


@app.route('/')
def index():
    """Renders the brevet control-times page."""
    return render_template('calc.html')


@app.route('/_calc_times')
def _calc_times():
    """Calculates open and close times for one control.

    Expects km, brevet_dist, and start_time as query arguments.
    """
    km = request.args.get('km', 0, type=float)
    brevet_dist = request.args.get('brevet_dist', 200, type=int)
    start_time = request.args.get('start_time', type=str)

    open_t = acp_times.open_time(km, brevet_dist, start_time)
    close_t = acp_times.close_time(km, brevet_dist, start_time)
    result = {"open": open_t, "close": close_t}
    return jsonify(result=result)


@app.route('/submit', methods=['POST'])
def submit():
    """Stores filled control rows in MongoDB.

    Returns an error and writes nothing when controls are missing or invalid.
    A successful submit replaces the previously stored list.
    """
    payload = request.get_json(silent=True)
    controls = []
    if isinstance(payload, dict) and isinstance(payload.get('controls'), list):
        controls = payload['controls']

    rows = []
    prev_km = -1.0
    for row in controls:
        if not isinstance(row, dict):
            continue
        km_raw = row.get('km')
        if km_raw is None or str(km_raw).strip() == '':
            continue
        try:
            km = float(km_raw)
        except ValueError:
            return jsonify(error="Control distance must be a number"), 400

        if km < 0 or km > 1200:
            return jsonify(error="Control distance out of valid range (0-1200 km)"), 400
        if km < prev_km:
            return jsonify(error="Control distances must be in non-decreasing order"), 400
        prev_km = km

        open_t = str(row.get('open', '')).strip()
        close_t = str(row.get('close', '')).strip()
        if not open_t or not close_t:
            return jsonify(error="Missing open or close time for control"), 400

        rows.append({
            'miles': row.get('miles', ''),
            'km': str(km_raw).strip(),
            'location': row.get('location', ''),
            'open': open_t,
            'close': close_t,
        })

    if not rows:
        return jsonify(error="No control times to submit"), 400

    db.tododb.delete_many({})
    for row in rows:
        db.tododb.insert_one(row)

    return jsonify(message="Stored {} controls".format(len(rows)))


@app.route('/display')
def display():
    """Shows the control times currently stored in the database."""
    items = list(db.tododb.find())
    return render_template('display.html', items=items)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)