from flask_login import UserMixin
from main import mysql, login_manager

class User(UserMixin):
    def __init__(self, id, name, password, email, role):
        self.id = id
        self.name = name
        self.password = password  # agora é a senha em texto simples
        self.email = email
        self.role = role

    def check_password(self, password):
        # Comparação direta com a senha armazenada
        return self.password == password

def get_user_by_email(email):
    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],  # senha em texto simples
            role=user_data['role']
        )
    return None

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],  # senha em texto simples
            role=user_data['role']
        )
    return None
