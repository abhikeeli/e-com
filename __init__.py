from flask import Flask
from db import db, db_init  # Import db and db_init
from auth import auth       # Import blueprints
from main import main

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
    app.config['SECRET_KEY'] = 'mandhitenalirasamiiiiiiabbbbhi'

    # Initialize the database
    db_init(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app


apps = create_app()

if __name__ == "__main__":
    apps.run(debug=True)











    









       



        






