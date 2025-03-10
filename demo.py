from huey import SqliteHuey
from huey import crontab
from flask import Flask, jsonify, request

huey = SqliteHuey(filename='/tmp/demo.db')
app = Flask(__name__)

@huey.task()
def add(a, b):
    return a + b

@app.route('/test', methods=['GET'])
@huey.periodic_task(crontab(minute='*/3'))
def every_three_minutes():
    print('This task runs every three minutes')
    return 'hi'
