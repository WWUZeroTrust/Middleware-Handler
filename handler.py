from flask import Flask, jsonify, request, abort
import requests
import json
import threading

user = ""
score = ""
resource = ""
lock = threading.Event()

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

    try:
        return requests.put(url, headers=headers, data=value)
    except:
        return ""
def opa_query ():
    headers = {
        'Content-Type': 'application/json'
    }
    url = 'http://localhost:8181/v1/data/rbac/authz/allow'
    null = ""
    data = '{"input":{"user": "%s", "action": "write", "object": "%s", "score": "%s"%s}%s}' %(user, resource, score, null, null)
    print(data)
    response = requests.post(url, headers=headers, data=data)
    try:
        return(response.text)
    except:
        return ""

def get_user(value):
    global user 
    user = value

def get_score(value):
    global score
    score = value

def get_resource(value):
    global resource
    resource = value

@app.route('/<int:task_id>', methods=['GET'])
def Query_routine(task_id):
    global lock
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
            abort(502)

        #Wait for lock to open. This waits for a new score to be pushed from TrustAPI
        lock.wait()


        query2 = opa_query()
        if str(query2) != '{"result":true}':
            print("query2:%s" %query2)
            print("Unknown error. Either access was denied or there was a failed connection to Open Policy Agent")
            abort(401)

        #After the OPA has evaluated all fields, the lock is set to closed, and waits for a new updated score. 


        return jsonify({'tasks': tasks})

lock.clear()

@app.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)

    tasks[0]['value'] = request.json.get('value', tasks[0]['value'])

    if task_id == 2:
        get_score(tasks[0]['value'])
        global lock
        lock.set()
        print("Lock is set to open")

    return jsonify({'tasks': tasks[0]})

if __name__ == "__main__":
    app.run(host='192.168.1.103',port=5000, debug=True)

#Query Command
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"JWT\":\"VALUE\"}" http://localhost:5000/1

# curl -i http://localhost:5000/1