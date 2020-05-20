__author__ = 'nilayshah'

from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
from consul.consul_schema import schema
import alchemy_new as Database
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/graphql.json": {"origins": "*"}}) # CORS used for what?
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

app.add_url_rule('/graphql.json', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

database_object = Database.Database()
database_object.create_tables()

path = "/home/app/data/credentials.json"
file_exists = os.path.isfile(path)
if file_exists:
    os.remove(path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass
