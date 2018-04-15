from bottle import route, run, template
from os import getenv


PORT = getenv('PORT', 8080)
HOST = getenv('IP', '0.0.0.0')


@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)


run(host=HOST, port=PORT)
