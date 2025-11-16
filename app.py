from flask import Flask

app = Flask(__name__)  


@app.route('/tasks', methods=['POST'])
def create_task():
    return {"message": "Method not implemented"}, 501

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return {"message": "Method not implemented"}, 501

@app.route('/tasks/:id', methods=['DELETE'])
def delete_tasks():
    return {"message": "Method not implemented"}, 501

@app.route('/tasks/:id/complete', methods=['GET'])
def complete_task():
    return {"message": "Method not implemented"}, 501

if __name__ == '__main__':
    app.run(debug=True)