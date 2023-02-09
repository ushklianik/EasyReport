import os
import logging
from flask            import Flask

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

if (os.path.exists("./app/logs/info.log") == False):
    f = open("./app/logs/info.log", "w")
logging.basicConfig(filename='./app/logs/info.log', level=logging.INFO)

app.config['SECRET_KEY'] = "secret_key"

# Import routing, models and Start the App
from app import views

