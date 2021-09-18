from flask import Flask, url_for, request
app = Flask(__name__)

@app.route('/')
def index():
    return 'Plantchecker API'

@app.route('/login/')
def login(): pass

@app.route('/user/<username>')
def user(username): pass

@app.route('/calc/', methods = ['POST'])
def calc():
    json = request.get_json()
    result = json['a']+json['b']
    return f'Был получен {request.method} запрос. Результат - {result}\n'

with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('user',username='linlynx'))


if __name__ == '__main__':
    app.run(debug=True)