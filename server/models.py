from sqlalchemy.orm import validates
from marshmallow import Schema, fields
from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    # Relationship: User has many Recipes
    recipes = db.relationship('Recipe', backref='user')

    # Property to prevent direct access to the password hash
    @property
    def password_hash(self):
        raise AttributeError("password_hash is not accessible")

    # Setter to hash the password before storing it
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Method to verify the password
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    # Relationship: Recipe belongs to a User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Custom validation for instructions length
    @validates('instructions')
    def validate_instructions(self, key, value):
        if value is None or len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return value


# Marshmallow Schemas for Serialization
class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    image_url = fields.String()
    bio = fields.String()

class RecipeSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    instructions = fields.String()
    minutes_to_complete = fields.Integer()
    user = fields.Nested(UserSchema)