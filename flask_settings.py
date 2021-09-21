from flask import Flask, request, jsonify
from plantchecker import Plantchecker

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return 'Plantchecker API'


@app.route('/login/')
def login(): pass


@app.route('/users/')
def add_user(): pass


# create user plant with spec and last watering and last fertiling dates
@app.route('/plants/', methods=['POST', 'DELETE'])
def plants():
    json = request.get_json()
    if request.method == 'POST':
        return Plantchecker.add_user_plant(json)
    else:
        pass


# get json list of user's plants
@app.route('/plants/list/', methods=['GET'])
def usercard():
    username = request.args.get('username',default = None, type = str)
    id = request.args.get('user_id',default = None, type = int)
    return jsonify(Plantchecker.check_user_plants(username,id))


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be today
@app.route('/plants/water/', methods=['PUT'])
def water():
    json = request.get_json()
    return Plantchecker.add_plant_water(json)


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be today
@app.route('/plants/fertilew/', methods=['PUT'])
def fertile():
    json = request.get_json()
    return Plantchecker.add_plant_fertile(json)

with app.test_request_context():
        print("it's working")
        print(app.url_map)


if __name__ == '__main__':
    app.run(port=5000,debug=True)
    with app.test_request_context():
        print("it's working")
        print(app.url_map)
