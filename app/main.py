from flask import Flask
from flask_cors import CORS
from routes import register_routes
import config

app = Flask(__name__)
CORS(app)

register_routes(app)