from flask import Flask, jsonify, request
from flask_cors import CORS
from api_data import get_premier_league_standing, get_premier_league_fixtures
from utils import load_pkl

test_standing = load_pkl('../data/pl22.pkl')
test_fixture = load_pkl('../data/fixtures.pkl')

app = Flask(__name__)
CORS(app)

# Define your routes and API endpoints here
@app.route('/', methods=['GET'])
def test():
    return jsonify(message='api is working')

@app.route('/premier-league/table', methods=['GET'])
def get_premier_league_table():
    # return jsonify(get_premier_league_standing().to_json(orient='records', index=False))
    return jsonify(test_standing.to_json(orient='records', index=False))

@app.route('/premier-league/fixtures', methods=['GET'])
def get_premier_league_fixtures():
    # return jsonify(get_premier_league_fixtures().to_json(orient='records', index=False))
    return jsonify(test_fixture.to_json(orient='records', index=False))

if __name__ == '__main__':
    app.run(debug=True, port=9102)
