from flask import Flask, request, jsonify, url_for
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
@app.route('/plants/', methods=['POST', 'DELETE', 'GET'])
def plants():
    if request.method == 'POST':
        json = request.get_json()
        return Plantchecker.add_user_plant(json)
    elif request.method == 'GET':
        username = request.args.get('user', default=None)
        userid = request.args.get('user_id', default=None)
        return jsonify(Plantchecker.check_user_plants(username, userid))
    elif request.method == 'DELETE':
        plantname = request.args.get('plantname', default=None)
        login = request.args.get('login', default=None)
        plant_id = request.args.get('plant_id')
        user_id = request.args.get('user_id')
        return Plantchecker.delete_plant(plantname, login=login, plant_id=plant_id, user_id=user_id)
    else:
        return 'Здесь доступ к списку растений пользователей'


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be today
@app.route('/plants/water/', methods=['PUT'])
def water():
    json = request.get_json()
    return Plantchecker.add_plant_water(json)


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be today
@app.route('/plants/fertile/', methods=['PUT'])
def fertile():
    json = request.get_json()
    return Plantchecker.add_plant_fertile(json)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
    print(url_for('plants', user='linlynx'))
    with app.test_context():
        url_for('plants', user='linlynx')
        # print("it's working")
        # print(app.url_map)
