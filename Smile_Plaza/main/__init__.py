from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from main.config import Config



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from main.users.routes import users
    from main.posts.routes import posts
    from main.errors.handlers import errors
    from main.appointment.routes import appointment
    from main.main1.routes import main1
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)
    app.register_blueprint(appointment)
    app.register_blueprint(main1)

    return app