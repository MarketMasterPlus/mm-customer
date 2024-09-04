# mm-customer/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from dotenv import load_dotenv
import os

# Create a shared instance of SQLAlchemy and Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Set configuration for the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    # Initialize the database and migration engine with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register API routes
    from .api.routes import blueprint as api_blueprint
    app.register_blueprint(api_blueprint)

    # Configure Swagger
    from .swagger import configure_swagger
    configure_swagger(app)

    return app
