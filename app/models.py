# Copyright 2023 Uladzislau Shklianik <ushklianik@gmail.com> & Siamion Viatoshkin <sema.cod@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from app         import db
from flask_login import UserMixin
from datetime    import datetime


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id            = db.Column(db.Integer, primary_key=True)
    user          = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(120), unique=True)
    password      = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user     = user
        self.password = password
        self.email    = email

    def __repr__(self):
        return f'{self.id} - {self.user}'

    def save(self):
        # inject self into db session
        db.session.add(self)
        # commit change and save the object
        db.session.commit()
        return self


class Credentials(db.Model):
    __tablename__ = 'Credentials'
    id            = db.Column(db.Integer, primary_key=True)
    key           = db.Column(db.String(120), unique=True)
    value         = db.Column(db.String(500))

    def __init__(self, value, key):
        self.key   = f"token_in_sql:{datetime.now().timestamp()}"
        self.value = value

    def __repr__(self):
        return f'{self.id} - {self.key}'

    def save(self):
        # inject self into db session
        db.session.add(self)
        # commit change and save the object
        db.session.commit()
        return self.key


    @classmethod
    def get(cls, key):
        result = db.session.query(cls).filter_by(key=key).first()
        if result:
            return result.value
        else:
            return "Token not found"


    @classmethod
    def delete(cls, key):
        db.session.query(cls).filter_by(key=key).delete()