from flask import Flask, url_for, request, jsonify
from plantchecker import Plantchecker
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# create/delete login, create/delete plant, getuserplants, update water/fertile


@app.route('/')
def index():
    return 'Plantchecker API'


@app.route('/login/')
def login(): pass


@app.route('/user/<username>', methods=['GET'])
def usercard(username):
    return jsonify(Plantchecker.checkUserPlants(username))


@app.route('/calc/', methods=['POST'])
def calc():
    json = request.get_json()
    result = json['a']+json['b']
    return f'Был получен {request.method} запрос. Результат - {result}\n'


with app.test_request_context():
    print(url_for('index'))
    print(url_for('usercard', username='linlynx'))
    print(url_for('calc'))


if __name__ == '__main__':
    app.run(debug=True)
