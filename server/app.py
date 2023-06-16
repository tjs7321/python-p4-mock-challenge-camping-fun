#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")


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
        try:
            campers = [camper.to_dict(only=("id", "name", "age"))
                       for camper in Camper.query.all()]

            return campers, 200

        except:
            return {"error": "Bad request"}, 400

    def post(self):

        # request = request.get_json()
        try:
            new_camper = Camper(
                name=request.json['name'],
                age=request.json['age']
            )
            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(only=("id", "name", "age")), 201
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Campers, "/campers")


class CampersById(Resource):

    def get(self, id):
        # pass
        try:
            camper = Camper.query.filter(Camper.id == id).first().to_dict(
                only=("id", "name", "age", "activities"))

            # print(camper)
            return camper, 200
        except:
            return {"error": "404: Camper not found"}, 404

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).one_or_none()

        if camper == None:
            return {'error': 'Camper not found'}, 404

        fields = request.get_json()

        try:
            for key in fields:
                setattr(camper, key, fields[key])

            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(rules=('-signups',)), 202

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(CampersById, "/campers/<int:id>")


class Activities(Resource):

    def get(self):
        try:
            activities = [activity.to_dict()
                          for activity in Activity.query.all()]
            return activities, 200
        except:
            return {
                'error': 'Bad request'
            }, 400


api.add_resource(Activities, "/activities")


class ActivititesById(Resource):

    def delete(self, id):
        try:
            activity = Activity.query.filter_by(id=id).first()

            db.session.delete(activity)
            db.session.commit()

            return {}, 204
        except:
            return {"error": "404: Activity not found"}, 404


api.add_resource(ActivititesById, "/activities/<int:id>")


class Signups(Resource):

    def post(self):
        try:
            signup = Signup(
                time=request.json["time"],
                camper_id=request.json["camper_id"],
                activity_id=request.json["activity_id"]
            )

            db.session.add(signup)
            db.session.commit()

            return signup.activity.to_dict(), 201

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
