class Config:
    # Configurações básicas
    SECRET_KEY = 'MMM-s'  # Chave para sessões e tokens
    DEBUG = False  # Desativado em produção
    
    # Configurações do MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'mmm-s'
    
    # Configurações de upload (se necessário)
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite de 16MB para uploads
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos em segundos

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # Em produção, você deve mudar estas configurações:
    # SECRET_KEY = 'uma-chave-muito-segura-e-diferente'
    # MYSQL_PASSWORD = 'senha-segura-do-banco'

# Config atual
config = Config()