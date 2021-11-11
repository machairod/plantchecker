from flask import Flask, request, jsonify, url_for
from plantchecker import Plantchecker

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return 'Plantchecker API'


@app.route('/users/')
def login():
    if request.method == 'POST':
        json = request.get_json()
        return Plantchecker.add_user(json)
    elif request.method == 'GET':
        username = request.args.get('login', default=None)
        if username is None:
            return 'Здесь проверка пользователей'
        else: return jsonify(Plantchecker.check_user(username))



# create user plant with spec and last watering and last fertiling dates
@app.route('/plants/', methods=['POST', 'DELETE', 'GET'])
def plants():
    if request.method == 'POST':
        json = request.get_json()
        return Plantchecker.add_user_plant(json)
    elif request.method == 'GET':
        username = request.args.get('login', default=None)
        userid = request.args.get('user_id', default=None)
        if userid is None and username is None:
            return 'Здесь доступ к списку растений пользователей'
        else: return jsonify(Plantchecker.check_user_plants(username, userid))
    elif request.method == 'DELETE':
        plantname = request.args.get('plantname', default=None)
        username = request.args.get('login', default=None)
        plant_id = request.args.get('plant_id')
        user_id = request.args.get('user_id')
        return Plantchecker.delete_plant(plantname, login=username, plant_id=plant_id, user_id=user_id)
    else:
        return 'Здесь доступ к списку растений пользователей'


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be today
@app.route('/plants/water/', methods=['PUT'])
def water():
    json = request.get_json()
    return Plantchecker.add_plant_water(json)


# update last_watering date for user plant
# json must contain at least 'name' and likely, a date, if not it would be on date
@app.route('/plants/fertile/', methods=['PUT'])
def fertile():
    json = request.get_json()
    return Plantchecker.add_plant_fertile(json)


if __name__ == '__main__':
    app.run(port=5000, debug=True)

