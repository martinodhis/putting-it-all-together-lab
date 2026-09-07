#!/usr/bin/env python3
from flask import request, session
from flask_restful import Resource
from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

class Signup(Resource):
    def post(self):
        json_data = request.get_json()
        try:
            new_user = User(
                username=json_data.get('username'),
                bio=json_data.get('bio'),
                image_url=json_data.get('image_url')
            )
            # The setter in the model will handle the bcrypt hashing
            new_user.password_hash = json_data.get('password')
            
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
        
        # Auto-login the user upon successful signup
        session['user_id'] = new_user.id
        return UserSchema().dump(new_user), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return UserSchema().dump(user), 200
        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200
            
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id', None)
            return {}, 204
        return {"error": "Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        
        recipes = Recipe.query.all()
        return RecipeSchema(many=True).dump(recipes), 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        
        json_data = request.get_json()
        try:
            new_recipe = Recipe(
                title=json_data.get('title'),
                instructions=json_data.get('instructions'),
                minutes_to_complete=json_data.get('minutes_to_complete'),
                user_id=user_id
            )
            db.session.add(new_recipe)
            db.session.commit()
            return RecipeSchema().dump(new_recipe), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

# Register Resources to API
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)