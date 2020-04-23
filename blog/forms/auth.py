from flask import Flask, render_template, jsonify,request
from flask_cors import CORS

from ..extensions import db
from flask_sqlalchemy import SQLAlchemy
from ..config import Config
from werkzeug.security import generate_password_hash
from ..model import user
"""
app = Flask(__name__)
app.config.from_object(Config['development'])
cors = CORS(app, resources={"/signinData/*": {"origins": "*"}})    #/signinData/*
db = SQLAlchemy(app)
"""




