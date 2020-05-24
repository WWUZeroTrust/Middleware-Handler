from flask import Flask, jsonify, request
import requests
import time


app = Flask(__name__)
#Need user, score, and resource for OPA query
tasks = [
    {
        'id': 1,
        'value': u'user'
    },
    {
        'id': 2,
        'value': u'score'
    },
    {
        'id': 3,
        'value': u'resource'
    }
]

# function to post user to trust api. 
def trust_query( url, value ):

    headers = {
        'Content-Type': 'application/json'
    }

    return requests.put(url, headers=headers, data=value)

def get_user(value):
    print("Put value: %s" %value)

def get_score(value):
    print("Put value: %s" %value)

def get_resource(value):
    print("Put value: %s" %value)

@app.route('/<int:task_id>', methods=['GET', 'PUT'])
def update_task(task_id):

    if request.method == 'GET':

        print(request.headers['Remote-User'])
        print(request.headers['X-Forwarded-Host'])

        #Json format for windows commandline user = r"{\"value\":\"%s\"}" % request.headers['Remote-User']

        #grabs the user from traifik get request
        user1 = '{"value": "%s"}' %request.headers['Remote-User']

        #Push the username to the trust API
        query1 = trust_query('http://192.168.1.103:5001/1', user1)

        #prints out the response from trust api. 
        #Need to implement continue if response = 200
        print("query1: %s" %query1)

        return jsonify({'tasks': tasks})

    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)

    tasks[0]['value'] = request.json.get('value', tasks[0]['value'])
    
    if task_id == 1:
        get_user(tasks[0]['value'])
    if task_id == 2:
        get_score(tasks[0]['value'])
    if task_id == 3:
        get_resource(tasks[0]['value'])

    #time.sleep(5)
    return jsonify({'tasks': tasks[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(host='192.168.1.103',port=5000, debug=True)

#Query Command
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"JWT\":\"VALUE\"}" http://localhost:5000/1

# curl -i http://localhost:5000/1