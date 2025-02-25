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
        campers = [camper.to_dict(rules=('-signups',))
                for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        try:
            new_camper = Camper(
                name=request.json['name'],
                age=request.json['age']
            )
            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(rules=('-signups',)), 201
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Campers, '/campers')

class CampersByID(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(), 200)
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        data = request.get_json()
        try:
            setattr(camper, 'name', data['name'])
            setattr(camper, 'age', data['age'])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(rules=('-signups',)), 202
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

    
api.add_resource(CampersByID, '/campers/<int:id>')

class Activities(Resource):

    def get(self):
        activities = [activity.to_dict(rules=('-signups',))
                    for activity in Activity.query.all()]
        return make_response(activities, 200)
    
api.add_resource(Activities, '/activities')

class ActivitiesByID(Resource):

    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        return make_response({"error": "Activity not found"}, 404)
    
api.add_resource(ActivitiesByID, '/activities/<int:id>')

class Signups(Resource):
    
    def post(self):
        try:
            new_signup = Signup(
                time=request.json['time'],
                camper_id=request.json['camper_id'],
                activity_id=request.json['activity_id']
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
