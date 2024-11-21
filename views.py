# Imports
import json
import os
from flask import render_template, redirect, request, flash, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user, login_required
from models import get_user_by_email, create_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
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
        return redirect(url_for('cadastro'))
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
    pdf = request.files.get('pdf')  # Obter o PDF do formulário

    # Verifica se o arquivo de imagem existe e se tem uma extensão válida
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        image_url = f"/static/uploads/{image_filename}"  # Caminho para acessar a imagem no HTML
    else:
        image_url = None  # Se não houver imagem ou a extensão for inválida, define como None

    # Verifica se o arquivo PDF existe e se tem uma extensão válida
    if pdf and allowed_file(pdf.filename, ['pdf']):
        pdf_filename = secure_filename(pdf.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf.save(pdf_path)
        pdf_url = f"/static/uploads/{pdf_filename}"  # Caminho do PDF
    else:
        pdf_url = None

    # Carregar o arquivo JSON
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []

    # Gerar ID único
    card_id = max([card['id'] for card in cards], default=-1) + 1  # Garantir que o ID seja único

    # Criar o novo card
    new_card = {
        "id": card_id,  # Adicionando o ID
        "name": data['name'],
        "model": data['model'],
        "year": data['year'],
        "price": data['price'],
        "sector": data['sector'],
        "category": data['category'],
        "status": data['status'],
        "description": data.get('description', 'Sem descrição'),  # Incluindo descrição padrão, se não fornecida
        "image_url": image_url,  # Caminho da imagem, se disponível
        "pdf_url": pdf_url  # Caminho do PDF, se disponível
    }

    # Adicionar o novo card à lista e salvar no JSON
    cards.append(new_card)
    with open('cards.json', 'w') as file:
        json.dump(cards, file, indent=4)

    return jsonify({"message": "Card salvo com sucesso!", "image_url": image_url, "pdf_url": pdf_url})


# Função para verificar extensões de arquivo permitidas
def allowed_file(filename, allowed_extensions=['png', 'jpg', 'jpeg', 'pdf']):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Chama os cards
@app.route('/load_cards', methods=['GET'])
def load_cards():
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
    except FileNotFoundError:
        cards = []
    
    return jsonify(cards)

# Rota para a página de detalhamento de um card específico
@app.route('/detalhamento/<int:card_id>', methods=['GET'])
def detalhamento(card_id):
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
        
        # Buscar o card com o ID fornecido
        card = next((card for card in cards if card['id'] == card_id), None)
        
        if card is None:
            return "Card não encontrado", 404
        
        # Renderiza a página de detalhamento, passando o card encontrado
        return render_template('detalhamento.html', card=card)
    
    except FileNotFoundError:
        return "Arquivo cards.json não encontrado", 404

@app.route('/bento/<int:card_id>', methods=['GET'])
def bento(card_id):
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
        
        # Buscar o card com o ID fornecido
        card = next((card for card in cards if card['id'] == card_id), None)
        
        if card is None:
            return "Card não encontrado", 404
        
        # Renderiza a página bento, passando o card encontrado
        return render_template('bento.html', card=card)
    
    except FileNotFoundError:
        return "Arquivo cards.json não encontrado", 404


@app.route('/download_cuidados/<int:card_id>', methods=['GET'])
def download_cuidados(card_id):
    try:
        with open('cards.json', 'r') as file:
            cards = json.load(file)
        
        card = next((card for card in cards if card['id'] == card_id), None)
        if not card:
            return "Card não encontrado", 404

        # Criar o PDF
        pdf_path = f"static/uploads/cuidados_{card_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Título
        c.drawString(100, 750, f"PDF do Histórico de Manutenção - {card['name']} ({card['model']})")

        # Informações da máquina
        c.drawString(50, 700, f"Marca/Modelo: {card['name']}")
        c.drawString(50, 680, f"Ano de Fabricação: {card['year']}")
        c.drawString(50, 660, f"Status: {card['status']}")
        c.drawString(50, 640, f"Equipamento: {card['category']}")
        c.drawString(50, 620, f"Valor de Aquisição: {card['price']}")
        c.drawString(50, 600, f"Localização: {card['sector']}")
        c.drawString(50, 580, f"Descrição: {card.get('description', 'Sem descrição')}")

        # Histórico de manutenção fictício
        historico = [
            ["Data", "Tipo", "Problema", "Ação", "Responsável", "Custo"],
            ["01/01/2023", "Preventiva", "Inspeção geral", "Verificação de peças", "João Silva", "R$ 200,00"],
            ["15/02/2023", "Corretiva", "Motor travado", "Troca de rolamento", "Maria Oliveira", "R$ 500,00"],
            ["20/03/2023", "Preventiva", "Lubrificação", "Engrenagens lubrificadas", "Carlos Mendes", "R$ 150,00"]
        ]

        # Adicionar o título da seção do histórico
        c.drawString(50, 540, "Histórico de Manutenção:")

        # Configurar a tabela no PDF
        table = Table(historico)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        # Inserir a tabela no PDF
        table.wrapOn(c, 50, 400)
        table.drawOn(c, 50, 400)

        # Finalizar e salvar o PDF
        c.save()
        return send_file(pdf_path, as_attachment=True)
    
    except FileNotFoundError:
        return "Arquivo cards.json não encontrado", 404