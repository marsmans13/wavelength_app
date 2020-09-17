from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config


app = Flask(__name__, instance_relative_config=True)
config = Config()
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from flask_uploads import UploadSet, configure_uploads, IMAGES


photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = '/tmp'
configure_uploads(app, photos)


from app.auth import auth_bp
from app.server import profile_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')

if __name__ == "__main__":
    # connect_to_db(app)

    app.run()