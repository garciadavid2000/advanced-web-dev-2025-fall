from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///streaks.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()  # for dev; in prod you'd use migrations

    return app

app = create_app()

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