#!/usr/bin/python3

# Runs on port 5000

import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

data = [{'id': 0, 'message': 'Hello World'}]

# Return plain message
@app.route("/hello", methods=['GET'])
def hello():
    return "Hello World!"

# Return json data
@app.route('/hello/api', methods=['GET'])
def hello_api():
    return jsonify(data)

if __name__ == '__main__':
    app.run()
