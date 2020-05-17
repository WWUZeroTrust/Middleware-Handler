from flask import Flask, jsonify, request


app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'value': u'test'
    },
    {
        'id': 2,
        'value': u'score'
    }
]

#Need to implement PUT. The Handler will pass JWT here.
@app.route('/<int:task_id>', methods=['GET', 'PUT'])
def update_task(task_id):

    if request.method == 'GET':
        return jsonify({'tasks': tasks})
    
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    
    tasks[0]['value'] = request.json.get('value', tasks[0]['value'])
    return jsonify({'tasks': tasks[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(debug=True)

#Query Command
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"JWT\":\"VALUE\"}" http://localhost:5000/1

# curl -i http://localhost:5000/1