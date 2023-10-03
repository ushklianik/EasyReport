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

import os
import logging

from flask            import Flask, g, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login      import LoginManager, current_user
from flask_bcrypt     import Bcrypt


# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# List of routes that do not require authentication
no_auth_required_routes = ['login', 'register', 'static']

@app.before_request
def check_authentication():
    g.user = current_user
    if not g.user.is_authenticated and request.endpoint not in no_auth_required_routes:
        return redirect(url_for('login'))

# Create logs directory if it doesn't exist
log_directory = os.path.join(basedir, "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, "info.log")
if not os.path.exists(log_file):
    open(log_file, "w")

logging.basicConfig(filename=log_file, level=logging.INFO)

app.config.from_object('app.config.Config')

db = SQLAlchemy(app)  # flask-sqlalchemy
bc = Bcrypt(app)  # flask-bcrypt

lm = LoginManager()  # flask-loginmanager
lm.init_app(app)  # init the login manager

# Setup database
database_directory = os.path.join(basedir, "data")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database_directory+'/database.db'
@app.before_first_request
def initialize_database():
    db.create_all()

config_path = "./app/data/config.json"

# Import routing, models and Start the App
from app       import models
from app.views import (reporting, auth, integrations, nfrs, other, grafana, graphs)