from collections import OrderedDict
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME="myusername",
    MAIL_PASSWORD="my password"
)
mail = Mail(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba246'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
credittable = {"AA": ["Outstanding", 10], "AB": ["Excellent", 9], "BB": ["Very Good", 8],
               "BC": ["Good", 7], "CC": ["Above Average", 6], "CD": ["Average", 5],
               "FF": ["Poor", 0], "I": ["Incomplete", 0]}
credittable = OrderedDict(sorted(credittable.items()))
from codes.transcripts import routes
