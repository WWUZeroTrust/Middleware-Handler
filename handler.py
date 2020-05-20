from flask import Flask, jsonify, request
from urllib.parse import urlencode
import pycurl
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
def trust_query(url, value):

    crl = pycurl.Curl()
    crl.setopt(curl.URL, url)
    data = value
    pf = urlencode(data)

    crl.setopt(crl.POSTFIELDS, pf)
    crl.perform()
    crl.close()

@app.route('/<int:task_id>', methods=['GET', 'PUT'])
def update_task(task_id):

    if request.method == 'GET':
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        # The username might be in the headers.
        #
        print(request.headers['Remote-User'])
        print(request.headers['X-Forwarded-Host'])

        #Just made this, not sure if it works. This is the json data to pass in function trust_query
        user = "{\"value\":\" {} \"}".format(request.headers['X-Forwarded-Host'])

        #Push the username to the trust API
        trust_query('http://192.168.1.103:5001/1', user)

        return jsonify({'tasks': tasks})


    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)

    tasks[0]['value'] = request.json.get('value', tasks[0]['value'])
    #time.sleep(5)
    return jsonify({'tasks': tasks[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not foundasdflioj'}), 404)

if __name__ == "__main__":
    app.run(host='192.168.1.103',port=5000)
    app.run(debug=True)

#Query Command
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"JWT\":\"VALUE\"}" http://localhost:5000/1

# curl -i http://localhost:5000/1