# IMPORTS
from flask import Flask
from flask_login import LoginManager
from config import config
import mysql.connector 


# Configuration of app
app = Flask(__name__)
app.config.from_object(config)

# Donfigurantion of Login
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# MySQL connection
mysql = mysql.connector.connect(
    host = app.config['MYSQL_HOST'],
    user = app.config['MYSQL_USER'],
    password = app.config['MYSQL_PASSWORD'],
    database = app.config['MYSQL_DB'],
)

# Definindo a chave secreta para usar o flash
app.secret_key = 'MMM-s'

# Não mude esta import de lugar
from views import *

if __name__ == "__main__":
    app.debug = True
    app.run()