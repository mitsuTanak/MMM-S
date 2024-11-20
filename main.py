from flask import Flask
from flask_login import LoginManager
from config import config
import mysql.connector 

# Configuration of app
app = Flask(__name__)
app.config.from_object(config)

# Configuration of Login
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# MySQL connection

print("Conectando ao banco de dados MySQL...")
try:
    mysql = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
    )
    print("Conexão com o MySQL bem-sucedida!")
except mysql.connector.Error as err:
    print(f"Erro do MySQL: {err}")
except Exception as e:
    print(f"Erro inesperado: {e}")


# Definindo a chave secreta para usar o flash
app.secret_key = 'MMM-s'

# Não mude esta import de lugar
from views import *

if __name__ == "__main__":
    app.debug = True
    app.run()
