from flask import Flask
# import flask_login
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config


app = Flask(__name__, instance_relative_config=True)
"APPLICATION CREATED __INIT__"
config = Config()
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app.auth import auth_bp
from app.server import profile_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')

if __name__ == "__main__":
    # connect_to_db(app)

    app.run(debug=True)