from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

# Definindo a chave secreta para usar o flash
app.secret_key = 'mmms'

# Não mude esta import de lugar
from views import *

if __name__ == "__main__":
    app.run()