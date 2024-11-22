from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import mysql, get_db_connection
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, id, name, password_hash, email, role):
        """
        Inicializa um objeto User
        Args:
            id (int): ID do usuário
            name (str): Nome do usuário
            password_hash (str): Hash da senha
            email (str): Email do usuário
            role (str): Papel do usuário (administrator/supervisor/visitor)
        """
        self.id = id
        self.name = name
        self.password_hash = password_hash
        self.email = email
        self.role = role

    def check_password(self, password):
        """
        Verifica se a senha fornecida corresponde ao hash armazenado
        Args:
            password (str): Senha em texto puro para verificar
        Returns:
            bool: True se a senha estiver correta, False caso contrário
        """
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            logger.error(f"Erro na verificação da senha: {e}")
            return False
    
    def get_id(self):
        """
        Método necessário para Flask-Login
        Returns:
            str: ID do usuário como string
        """
        return str(self.id)

    @staticmethod
    def create(name, email, password, role):
        """
        Cria um novo usuário no banco de dados
        Args:
            name (str): Nome do usuário
            email (str): Email do usuário
            password (str): Senha em texto puro
            role (str): Papel do usuário (administrator/supervisor/visitor)
        Returns:
            bool: True se criado com sucesso, False caso contrário
        """
        try:
            # Verifica se o email já existe
            if User.get_by_email(email):
                logger.warning(f"Tentativa de criar usuário com email duplicado: {email}")
                return False

            cursor = mysql.cursor()
            password_hash = generate_password_hash(password)
            
            sql = """INSERT INTO usuarios (name, email, password, role) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (name, email, password_hash, role))
            mysql.commit()
            
            logger.info(f"Usuário criado com sucesso: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            mysql.rollback()
            return False
        finally:
            cursor.close()

    @staticmethod
    def get_by_email(email):
        """
        Busca um usuário pelo email
        Args:
            email (str): Email do usuário
        Returns:
            User: Objeto usuário se encontrado, None caso contrário
        """
        try:
            cursor = mysql.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data['role']
                )
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        """
        Busca um usuário pelo ID
        Args:
            user_id (int): ID do usuário
        Returns:
            User: Objeto usuário se encontrado, None caso contrário
        """
        try:
            cursor = mysql.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data['role']
                )
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def update_user(user_id, name=None, email=None, role=None):
        """
        Atualiza informações do usuário
        Args:
            user_id (int): ID do usuário a ser atualizado
            name (str, optional): Novo nome
            email (str, optional): Novo email
            role (str, optional): Novo papel
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            update_fields = []
            values = []
            
            if name:
                update_fields.append("name = %s")
                values.append(name)
            if email:
                update_fields.append("email = %s")
                values.append(email)
            if role:
                update_fields.append("role = %s")
                values.append(role)
                
            if not update_fields:
                return False
                
            values.append(user_id)
            sql = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor = mysql.cursor()
            cursor.execute(sql, values)
            mysql.commit()
            cursor.close()
            
            logger.info(f"Usuário {user_id} atualizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            mysql.rollback()
            return False

    @staticmethod
    def update_password(user_id, new_password):
        """
        Atualiza a senha do usuário
        Args:
            user_id (int): ID do usuário
            new_password (str): Nova senha em texto puro
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            cursor = mysql.cursor()
            password_hash = generate_password_hash(new_password)
            
            sql = "UPDATE usuarios SET password = %s WHERE id = %s"
            cursor.execute(sql, (password_hash, user_id))
            mysql.commit()
            cursor.close()
            
            logger.info(f"Senha atualizada com sucesso para usuário {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar senha: {e}")
            mysql.rollback()
            return False

    @staticmethod
    def delete_user(user_id):
        """
        Remove um usuário do sistema
        Args:
            user_id (int): ID do usuário a ser removido
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        try:
            cursor = mysql.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            mysql.commit()
            cursor.close()
            
            logger.info(f"Usuário {user_id} removido com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            mysql.rollback()
            return False

    @staticmethod
    def list_users():
        """
        Lista todos os usuários do sistema
        Returns:
            list: Lista de objetos User ou lista vazia em caso de erro
        """
        try:
            cursor = mysql.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios ORDER BY name")
            users_data = cursor.fetchall()
            cursor.close()
            
            return [User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data['password'],
                role=user_data['role']
            ) for user_data in users_data]
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []


# Cadastro de Maquinas
class Machine:
    def __init__(self, id, machine_name, model, manufacturing_year, price, sector, category, status, image_path=None, description=None):
        self.id = id
        self.machine_name = machine_name
        self.model = model
        self.manufacturing_year = manufacturing_year
        self.price = price
        self.sector = sector
        self.category = category
        self.status = status
        self.image_path = image_path
        self.description = description  # Novo atributo adicionado

    @staticmethod
    def get_all_machines():
        cursor = mysql.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM collection")
            machines = cursor.fetchall()
            return [Machine(**machine) for machine in machines]
        except Exception as e:
            print(f"Erro ao buscar máquinas: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def create_machine(machine_name, model, manufacturing_year, price, sector, category, status, image_path=None, description=None):
        cursor = mysql.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO collection (machine_name, model, manufacturing_year, price, sector, category, status, image_path, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (machine_name, model, manufacturing_year, price, sector, category, status, image_path, description),
            )
            mysql.commit()
        except Exception as e:
            print("Erro ao cadastrar máquina:", e)
            mysql.rollback()
        finally:
            cursor.close()
