from flask import Flask, request
from Kitchen import *
import json
import requests
cooks = json.load(open('cooks.json', 'r'))

app = Flask(__name__)

kitchen = Kitchen(cooks, 2, 1, 'menu.json')

@app.route('/order', methods=['POST'])
def order():
    data = request.json
    made_food = kitchen.prepare_food(data)
    requests.post('http://127.0.0.1:3000/distribution', json=made_food)
    return "finish"

app.run(port=2000, host= '0.0.0.0')