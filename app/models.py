# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app         import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id       = db.Column(db.Integer,     primary_key=True)
    user     = db.Column(db.String(64),  unique = True)
    email    = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user       = user
        self.password   = password
        self.email      = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):

        # inject self into db session    
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self 

class Credentials(db.Model):

    __tablename__ = 'Credentials'

    id       = db.Column(db.Integer,      primary_key=True)
    key      = db.Column(db.String(120),  unique = True)
    value    = db.Column(db.String(500))

    def __init__(self, key, value):
        self.key       = key
        self.value     = value

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.key)

    def save(self):

        # inject self into db session    
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self 
        
    @classmethod
    def get(cls, key):
        result = db.session.query(cls).filter_by(key=key).first()
        if result:
            return result.value
        else:
            return "Token not found"