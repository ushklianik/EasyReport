import os
import logging

from flask import Flask, g, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# List of routes that do not require authentication
no_auth_required_routes = ['login', 'register']

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
@app.before_first_request
def initialize_database():
    db.create_all()

# Import routing, models and Start the App
from app import models
from app.views import (reporting, auth, integrations, nfrs,
                       other, grafana, graphs)