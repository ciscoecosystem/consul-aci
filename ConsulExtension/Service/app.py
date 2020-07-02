from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
from schema import schema
import alchemy_core as database

app = Flask(__name__)
CORS(app, resources={r"/graphql.json": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

app.add_url_rule('/graphql.json', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

database_object = database.Database()
database_object.create_tables()


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass
