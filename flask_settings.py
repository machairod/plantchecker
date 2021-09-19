from flask import Flask, url_for, request, jsonify
from plantchecker import Plantchecker
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# create/delete login, create/delete plant, update water/fertile


@app.route('/')
def index():
    return 'Plantchecker API'


@app.route('/login/')
def login(): pass


# get json list of user's plants
@app.route('/user/<username>/', methods=['GET'])
def usercard(username):
    return jsonify(Plantchecker.checkUserPlants(username))


@app.route('/addwater/', methods=['PUT'])
def addwater():
    json = request.get_json()
    return Plantchecker.add_plant_water(json)



@app.route('/calc/', methods=['POST'])
def calc():
    json = request.get_json()
    result = json['a']+json['b']
    return f'Был получен {request.method} запрос. Результат - {result}\n'


with app.test_request_context():
    print("it's working")


if __name__ == '__main__':
    app.run(debug=True)
