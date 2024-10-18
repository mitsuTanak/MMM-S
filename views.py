# Onde estão as rotas
from flask import render_template, redirect, request, flash, url_for
from main import app
# rotas
@app.route("/home") 
def home():
    return render_template("home.html")

@app.route("/sobre") 
def sobre():
    return render_template("sobre.html")

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
