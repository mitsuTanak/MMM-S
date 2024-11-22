import mysql.connector
from config import config

def get_db_connection():
    print("Conectando ao banco de dados MySQL...")
    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
        )
        if connection.is_connected():
            print("Conexão com o MySQL bem-sucedida!")
        return connection
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

mysql = get_db_connection()