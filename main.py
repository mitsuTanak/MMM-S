from flask import Flask
from flask_login import LoginManager
from config import config
from models import User
from database import mysql
import mysql.connector 

# Configuration of app
app = Flask(__name__)
app.config.from_object(config)

# Configuration of Login
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# MySQL connection

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

app.secret_key = 'MMM-s'

# Não mude esta import de lugar
from views import *

if __name__ == "__main__":
    app.debug = True
    app.run()
