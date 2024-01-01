from flask import Flask, jsonify, request
from api_data import get_premier_league_standing
from utils import load_pkl

test_df = load_pkl('../data/pl22.pkl')

app = Flask(__name__)

# Define your routes and API endpoints here
@app.route('/', methods=['GET'])
def test():
    return jsonify(message='api is working')

# Example route with request parameters
@app.route('/premier-league/table', methods=['GET'])
def get_premier_league_table():
    # return jsonify(get_premier_league_standing().to_json(orient='records', index=False))
    return jsonify(test_df.to_json(orient='records', index=False))

if __name__ == '__main__':
    app.run(debug=True, port=9102)
