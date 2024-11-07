# Onde estão as rotas
import json
from flask import render_template, redirect, request, flash, url_for, jsonify
from main import app
# rotas
@app.route("/home") 
def home():
    return render_template("home.html")

@app.route("/sobre") 
def sobre():
    return render_template("sobre.html")

@app.route("/bento") 
def bento():
    return render_template("bento.html")


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Validação simples de email e senha
        if email == 'livia@gmail.com' and senha == '123':
            # Login bem-sucedido, redireciona para a página principal (home)
            return redirect(url_for('home'))
        else:
            # Flash message para usuário ou senha incorretos
            flash("E-mail ou senha incorretos", "error")
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route('/save_card', methods=['POST'])
def save_card():
    data = request.get_json()
    new_card = {
        "name": data['name'],
        "description": data['description']
    }
    
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []
    
    cards.append(new_card)
    
    with open('cards.json', 'w') as file:
        json.dump(cards, file)
    
    return jsonify({"message": "Card salvo com sucesso!"})

@app.route('/load_cards', methods=['GET'])
def load_cards():
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []
    
    return jsonify(cards)