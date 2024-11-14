# Imports
import json
import os
from flask import render_template, redirect, request, flash, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user, login_required
from models import get_user_by_email, create_user
from main import app


# Rotas

@app.route("/cadastrar_manutencao") 
def solucionar():
    return render_template("solucionar.html")

@app.route("/home") 
def home():
    return render_template("home.html")

@app.route("/sobre") 
def sobre():
    return render_template("sobre.html")

@app.route("/bento") 
def bento():
    return render_template("bento.html")


# Login

# Rota após o Login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Busca o usuário pelo email
        user = get_user_by_email(email)

        # Verifica a senha diretamente, sem hashing
        if user and user.password == password:
            login_user(user)
            if user.role == 'administrator':
                return redirect(url_for('home'))
            elif user.role == 'supervisor':
                return redirect(url_for('supervisor'))
            else:
                return redirect(url_for('sobre'))

        flash('E-mail ou senha incorretos')
        return redirect(url_for('login'))
        
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Cadastro

# Rota para a pagina de cadastro

@app.route("/cadastro", methods=['GET', 'POST']) 
def cadastro():

    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        senha = request.form.get('password')
        role = request.form.get('role')

        # Verifica se já existe
        if get_user_by_email(email):
            flash("Esse e-mail já está cadstrado")
            return redirect(url_for('cadastro'))
        
        # cria o usuario no banco de dados
        create_user(name=nome, email=email, password=senha, role=role)
        
        flash ('Cadastro realizado com SUCESSO!')
        return redirect(url_for('home'))
    return render_template("cadastro.html")




# Card

# Configuração do diretório de upload para as imagens
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para criar os cards

@app.route('/save_card', methods=['POST'])
def save_card():
    data = request.form
    image = request.files.get('image')  # Obter a imagem do formulário
    
    # Verifica se o arquivo de imagem existe e se tem uma extensão válida
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f"/{image_path}"  # Caminho para acessar a imagem no HTML
    else:
        image_url = None  # Se não houver imagem ou a extensão for inválida, define como None
    
    new_card = {
        "name": data['name'],
        "model": data['model'],
        "year": data['year'],
        "price": data['price'],
        "sector": data['sector'],
        "category": data['category'],
        "status": data['status'],
        "image_url": f'/static/uploads/{filename}'
    }
    
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []
    
    cards.append(new_card)
    
    with open('cards.json', 'w') as file:
        json.dump(cards, file)
    
    return jsonify({"message": "Card salvo com sucesso!", "image_url": image_url})

# Chama os cards
@app.route('/load_cards', methods=['GET'])
def load_cards():
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []
    
    return jsonify(cards)
