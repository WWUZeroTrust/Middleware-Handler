from flask import Flask, jsonify, request
import requests
import json
import time

user = ""
score = ""
resource = ""

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
def opa_query ():
    headers = {
        'Content-Type': 'application/json'
    }
    null = ""
    data = '{"input":{"user": "%s", "access": "write", "object": "%s", "score": "%s"%s}%s} ' %(user, resource, score, null, null)
    return requests.post('localhost:8181/v1/data/rbac/authz/allow', headers=headers, data=data)

def get_user(value):
    global user 
    user = value

def get_score(value):
    global score
    score = value

def get_resource(value):
    global resource
    resource = value

@app.route('/<int:task_id>', methods=['GET', 'PUT'])
def update_task(task_id):

    if request.method == 'GET':

        get_user(request.headers['Remote-User'])
        get_resource(request.headers['X-Forwarded-Host'])

        #Json format for windows commandline user = r"{\"value\":\"%s\"}" % request.headers['Remote-User']

        #grabs the user from traifik get request
        user1 = '{"value": "%s"}' %request.headers['Remote-User']

        #Calls function trust_query to PUT user into TurstAPI
        query1 = trust_query('http://192.168.1.103:5001/1', user1)

        if str(query1) != '<Response [200]>':
            print("query1:%s" %query1)
            print("Unknown error. Expected value is <Response [200]>")
            #For some reason when I return this response to traifik, It still continues as authenticated
            abort(404)
        #WHEN THIS FUNCTION IS CALLED. IT BREAKS. IT IS AN ISSUE WITH THE DATA VARIABLE IN opa_query(). Query needs to be sucessfull for traifik not to break. 
        print(opa_query())

        return jsonify({'tasks': tasks})

    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)

    tasks[0]['value'] = request.json.get('value', tasks[0]['value'])

    #Saves pushed values.
    if task_id == 2:
        get_score(tasks[0]['value'])

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