from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation import run_simulation
from routes import ROUTES
from behaviors import BEHAVIOR_PROFILES

app = Flask(__name__)
CORS(app)


@app.route('/api/routes', methods=['GET'])
def get_routes():
    return jsonify(list(ROUTES.keys()))


@app.route('/api/behaviors', methods=['GET'])
def get_behaviors():
    return jsonify(list(BEHAVIOR_PROFILES.keys()))


@app.route('/api/simulate', methods=['POST'])
def simulate():
    body = request.json or {}
    route_id      = body.get('route', 'route_1')
    behavior_name = body.get('behavior', 'Eco')

    if route_id not in ROUTES:
        return jsonify({'error': f'Unknown route: {route_id}'}), 400
    if behavior_name not in BEHAVIOR_PROFILES:
        return jsonify({'error': f'Unknown behavior: {behavior_name}'}), 400

    route    = ROUTES[route_id]
    behavior = BEHAVIOR_PROFILES[behavior_name]

    log, total_fuel, economy, distance_km = run_simulation(
        segments=route['segments'],
        behavior_name=behavior_name,
        behavior=behavior
    )

    return jsonify({
        'log':          log,
        'total_fuel_L': round(total_fuel, 6),
        'economy_kmL':  round(economy, 4),
        'distance_km':  round(distance_km, 4),
        'duration_s':   len(log),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
