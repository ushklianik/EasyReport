import os
import logging

from flask            import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login      import LoginManager
from flask_bcrypt     import Bcrypt

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

if not os.path.exists("./app/logs"):
    os.makedirs("./app/logs")
if not os.path.exists("./app/logs/info.log"):
    open("./app/logs/info.log", "w")

logging.basicConfig(filename='./app/logs/info.log', level=logging.INFO)

app.config.from_object('app.config.Config')

db = SQLAlchemy  (app) # flask-sqlalchemy
bc = Bcrypt      (app) # flask-bcrypt

lm = LoginManager(   ) # flask-loginmanager
lm.init_app(app)       # init the login manager

# Setup database
@app.before_first_request
def initialize_database():
    db.create_all()

# Import routing, models and Start the App
from app import models
from app.views import reporting
from app.views import auth
from app.views import integrations
from app.views import nfrs
from app.views import other
from app.views import grafana

