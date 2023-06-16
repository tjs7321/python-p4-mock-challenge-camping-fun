from models import Activity, Signup, Camper
from app import app, db
from faker import Faker
from flask import request
import json
import os
os.environ['DB_URI'] = "sqlite:///:memory:"


class TestApp:
    '''Flask application in app.py'''

    def test_gets_campers(self):
        '''retrieves campers with GET requests to /campers.'''

        with app.app_context():

            db.create_all()

            clark = Camper(name="Clark Kent", age=9)
            db.session.add(clark)
            db.session.commit()

            response = app.test_client().get('/campers').json
            campers = Camper.query.all()
            assert [camper['id'] for camper in response] == [
                camper.id for camper in campers]
            assert [camper['name'] for camper in response] == [
                camper.name for camper in campers]
            assert [camper['age'] for camper in response] == [
                camper.age for camper in campers]

    def test_gets_camper_by_id(self):
        '''retrieves one camper using its ID with GET request to /campers/<int:id>.'''

        with app.app_context():
            bruce = Camper(name="Bruce Wayne", age=11)
            db.session.add(bruce)
            db.session.commit()

            response = app.test_client().get(f'/campers/{bruce.id}').json
            assert response['name'] == bruce.name
            assert response['age'] == bruce.age

    def test_returns_404_if_no_camper(self):
        '''returns an error message and 404 status code when a camper is searched by a non-existent ID.'''

        with app.app_context():

            response = app.test_client().get('/campers/0')
            assert response.json.get('error')
            assert response.status_code == 404

    def test_creates_camper(self):
        '''creates one camper using a name and age with a POST request to /campers.'''

        with app.app_context():
            name = Faker().name()
            response = app.test_client().post(
                '/campers',
                json={
                    'name': name,
                    'age': 15
                }
            ).json

            assert response['id']
            assert response['name'] == name
            assert response['age'] == 15

            camper = Camper.query.filter(
                Camper.name == name, Camper.age == 15).one_or_none()
            assert camper

    def test_400_for_camper_validation_error(self):
        '''returns a 400 status code and error message if a POST request to /campers fails.'''

        with app.app_context():

            response = app.test_client().post(
                '/campers',
                json={
                    'name': 'Tony Stark',
                    'age': 19
                }
            )

            assert response.status_code == 400
            assert response.json['errors']

            response = app.test_client().post(
                'campers',
                json={
                    'name': '',
                    'age': 10
                }
            )

            assert response.status_code == 400
            assert response.json['errors']

    def test_patch_campers_by_id(self):
        '''updates campers with PATCH request to /campers/<int:id>.'''

        with app.app_context():
            camper = Camper(name=Faker().name(), age=10)
            db.session.add(camper)
            db.session.commit()

            response = app.test_client().patch(
                f'/campers/{camper.id}',
                json={
                    'name': camper.name + '(updated)',
                    'age': 11
                })

            assert response.status_code == 202
            assert response.content_type == 'application/json'
            response = response.json

            camper_updated = Camper.query.filter(
                Camper.id == camper.id).one_or_none()

            assert response['name'] == camper_updated.name
            assert '(updated)' in camper_updated.name
            assert response['age'] == 11
            camper_updated.age = 11

    def test_validates_camper_update(self):
        '''returns an error message if a PATCH request to /campers/<int:id>  is invalid.'''

        with app.app_context():
            fake = Faker()
            camper = Camper(name=fake.name(), age=10)
            db.session.add(camper)
            db.session.commit()

            response = app.test_client().patch(
                f'/campers/{camper.id}',
                json={
                    'name': '',
                    'age': 12
                })

            assert response.status_code == 400
            assert response.content_type == 'application/json'
            assert response.json['errors'] == ["validation errors"]

            response = app.test_client().patch(
                f'/campers/{camper.id}',
                json={
                    'name': 'valid name',
                    'age': 7
                })

            assert response.status_code == 400
            assert response.content_type == 'application/json'
            assert response.json['errors'] == ["validation errors"]

    def test_404_no_activity_to_patch(self):
        '''returns an error message if a PATCH request to /campers/<int:id> references a non-existent camper'''

        with app.app_context():

            response = app.test_client().patch(
                f'/campers/0',
                json={
                    'name': 'some name',
                    'age': 9
                })
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error')
            assert response.status_code == 404

    def test_gets_activities(self):
        '''retrieves activities with GET request to /activities'''

        with app.app_context():
            activity = Activity(name="Swimming", difficulty="4")
            db.session.add(activity)
            db.session.commit()

            response = app.test_client().get('/activities').json
            activities = Activity.query.all()

            assert [activity['id'] for activity in response] == [
                activity.id for activity in activities]
            assert [activity['name'] for activity in response] == [
                activity.name for activity in activities]
            assert [activity['difficulty'] for activity in response] == [
                activity.difficulty for activity in activities]

    def test_deletes_activities_by_id(self):
        '''deletes activities with DELETE request to /activities/<int:id>.'''

        with app.app_context():
            activity = Activity(name="Fire Building", difficulty="5")
            db.session.add(activity)
            db.session.commit()

            response = app.test_client().delete(f'/activities/{activity.id}')

            assert response.status_code == 204

            activity = Activity.query.filter(
                Activity.id == activity.id).one_or_none()
            assert not activity

    def test_returns_404_if_no_activity(self):
        '''returns 404 status code with DELETE request to /activities/<int:id> if activity does not exist.'''

        with app.app_context():
            response = app.test_client().delete('/activities/0')
            assert response.json.get('error')
            assert response.status_code == 404

    def test_creates_signups(self):
        '''creates signups with POST request to /signups'''

        with app.app_context():
            peter = Camper(name="Peter Parker", age=18)
            canoeing = Activity(name="Canoeing", difficulty=1)
            db.session.add_all([peter, canoeing])
            db.session.commit()

            response = app.test_client().post(
                '/signups',
                json={
                    'time': 12,
                    'camper_id': peter.id,
                    'activity_id': canoeing.id
                }
            ).json

            assert response['id']
            assert response['difficulty'] == 1
            assert response['name'] == 'Canoeing'

            signup = Signup.query.filter(
                Signup.id == response['id']).one_or_none()
            assert signup

    def test_400_for_signup_validation_error(self):
        '''returns a 400 status code and error message if a POST request to /signups fails.'''

        with app.app_context():
            peter = Camper(name="Peter Parker", age=18)
            canoeing = Activity(name="Canoeing", difficulty=1)
            db.session.add_all([peter, canoeing])
            db.session.commit()

            response = app.test_client().post(
                '/signups',
                json={
                    'time': 24,
                    'camper_id': peter.id,
                    'activity_id': canoeing.id
                }
            )

            assert response.status_code == 400
            assert response.json['errors']
