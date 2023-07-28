#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        return make_response([camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()], 200)
    
    def post(self):
        try:
            data = request.get_json()
            camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 200)
        except:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self, id):
        try:
            return make_response(Camper.query.filter_by(id=id).first().to_dict(), 200)
        except:
            return make_response({"error":"Camper not found"}, 404)

    def patch(self, id):
        try:
            camper = Camper.query.filter_by(id=id).first()
            data = request.get_json()
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.commit()
            return make_response(camper.to_dict(), 202)
        except AttributeError:
            return make_response({"error":"Camper not found"}, 404)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        return make_response([activity.to_dict() for activity in Activity.query.all()], 200)

api.add_resource(Activities, '/activities')

class ActivityById(Resource):
    def delete(self, id):
        try:
            activity = Activity.query.filter_by(id=id).first()
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        except:
            return make_response({"error":"Activity not found"}, 404)

api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        try:
            data = request.get_json()
            signup = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data['activity_id']
            )
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 200)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
