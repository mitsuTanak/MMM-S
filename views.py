# Imports
import json
import os
from flask import render_template, redirect, request, flash, url_for, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
from passlib.hash import scrypt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from main import app
from database import mysql
from models import User

# Configuração do diretório de upload para as imagens
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route("/supervisor")
@login_required
def supervisor():
    if current_user.role != 'supervisor' and current_user.role != 'administrator':
        flash('Acesso não autorizado', 'Erro')
        return redirect(url_for('home'))
    return render_template("supervisor.html")


# Login
# Rota após o Login
@app.route("/", methods=['GET', 'POST'])
def login():
    # Autenticação
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Por favor, preencha todos os campos', 'Erro')
            return redirect(url_for('login'))
        
        # Busca o usuário pelo email
        user = User.get_by_email(email)

        # Verifica a senha diretamente, sem hashing
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'administrator':
                return redirect(url_for('home'))
            elif user.role == 'supervisor':
                return redirect(url_for('supervisor'))
            else:
                return redirect(url_for('sobre'))

        flash('E-mail ou senha incorretos', 'error')
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
        nome = request.form.get('name')  # Corrigido para 'nome'
        email = request.form.get('email')  # Correto
        senha = request.form.get('password')  # Corrigido para 'senha'
        role = request.form.get('role')  # Correto

        print(f"Dados recebidos: nome={nome}, email={email}, role={role}")

        if not all([nome, email, senha, role]):
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('cadastro'))

        print(f"Dados recebidos: nome={nome}, email={email}, role={role}")  # Log para debug

        # Validações
        if not all([nome, email, senha, role]):
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('cadastro'))

        # Verifica se já existe
        if User.get_by_email(email):
            flash("Esse e-mail já está cadastrado")
            return redirect(url_for('cadastro'))
        # Cria o usuário no banco de dados, passando a senha criptografada (senha hash)
        try:
            # Tenta criar o usuário
            if User.create(name=nome, email=email, password=senha, role=role):
                flash('Cadastro realizado com sucesso!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Erro ao realizar cadastro. Tente novamente.', 'error')
        except Exception as e:
            print(f"Erro no cadastro: {str(e)}")  # Log para debug
            flash(f'Erro ao realizar cadastro: {str(e)}', 'error')

        flash('Cadastro realizado com SUCESSO!')

        return redirect(url_for('cadastro'))
    
    # Se for GET, simplesmente renderiza o template
    return render_template("cadastro.html")


# Card
# _________________________________________________________________________________________________
@app.route('/save_machine', methods=['POST'])
def save_machine():
    data = request.form
    image = request.files.get('image')  # Obter a imagem
    pdf = request.files.get('pdf')  # Obter o PDF

    # Salvar a imagem
    image_url = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        image_url = f"/static/uploads/{image_filename}"  # Caminho acessível no HTML

    # Salvar o PDF
    pdf_url = None
    if pdf and allowed_file(pdf.filename, extensions=['pdf']):
        pdf_filename = secure_filename(pdf.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf.save(pdf_path)
        pdf_url = f"/static/uploads/{pdf_filename}"  # Caminho acessível no HTML

    # Adicionar o campo de descrição
    description = data.get('card-description', None)  # Captura a descrição do formulário, se existir

    # Salvar as informações da máquina no banco de dados (tabela 'collection')
    cursor = mysql.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO collection (machine_name, model, manufacturing_year, price, sector, category, status, description, image_path, pdf_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (data['card-name'], data['card-model'], data['card-year'], data['card-price'],
             data['card-sector'], data['card-category'], data['card-status'],
             data.get('card-description'), image_url, pdf_url)
        )
        mysql.commit()

        machine_id = cursor.lastrowid  # Recupera o ID da máquina cadastrada
        response = {
            'id': machine_id,
            'image_url': image_url,
            'name': data['card-name']
        }
        return jsonify(response)

    except Exception as e:
        mysql.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


@app.route('/load_machines', methods=['GET'])
def load_machines():
    cursor = mysql.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM collection")
        machines = cursor.fetchall()

        # Debug: Verificando os dados recuperados
        print("Máquinas recuperadas do banco:", machines)

        return jsonify(machines)  # Retorne os dados como JSON para o frontend

    except Exception as e:
        print(f"Erro ao carregar máquinas: {e}")  # Log de erro detalhado
        flash(f'Erro ao carregar máquinas: {e}')  # Mostrar no flash
        return jsonify({'error': 'Erro ao carregar máquinas'}), 500  # Resposta de erro em JSON
    finally:
        cursor.close()


@app.route('/detalhamento/<int:machine_id>', methods=['GET'])
def detalhamento(machine_id):
    cursor = mysql.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM collection WHERE id = %s", (machine_id,))
        machine = cursor.fetchone()
        if machine:
            return render_template('detalhamento.html', card=machine)
        else:
            return "Máquina não encontrada", 404
    except Exception as e:
        print(f"Erro ao buscar detalhes da máquina: {e}")
        return "Erro ao carregar os detalhes.", 500
    finally:
        cursor.close()

# _______________________________________________________________________________________

@app.route('/bento/<int:card_id>', methods=['GET'])
def bento(card_id):
    cursor = mysql.cursor(dictionary=True)
    try:
        # Buscar dados da máquina
        cursor.execute("SELECT * FROM collection WHERE id = %s", (card_id,))
        card = cursor.fetchone()

        # Calcular o custo total por setor
        cursor.execute("""
            SELECT sector, SUM(price) as total_cost
            FROM collection
            GROUP BY sector
        """)
        sector_costs = cursor.fetchall()

        # Verifique se os dados estão sendo recuperados corretamente
        print("Dados de setor e custo: ", sector_costs)  # Verifique os dados no console

        # Transformar os dados em JSON antes de passar para o template
        sector_costs_json = json.dumps(sector_costs)

        if not card:
            return "Card não encontrado", 404

        # Passar os dados para o template
        return render_template('bento.html', card=card, sector_costs=sector_costs_json)
    
    except Exception as e:
        print(f"Erro ao buscar dados para o bento: {e}")
        return "Erro ao carregar os dados.", 500
    finally:
        cursor.close()
        
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
        c.setFont("Helvetica-Bold", 14)

        # Título
        c.drawString(200, 770, "FICHA DE MÁQUINAS E EQUIPAMENTOS")

        # Cabeçalho da ficha
        c.setFont("Helvetica", 15)
        c.drawString(50, 740, f"Denominação: {card['name']}")
        c.drawString(300, 740, f"Marca/Modelo: {card['model']}")
        c.drawString(50, 720, f"Nº de Série: {card.get('serial_number', 'N/A')}")
        c.drawString(300, 720, f"Ano de Fabricação: {card['year']}")
        c.drawString(50, 700, f"Seção: {card['sector']}")
        c.drawString(300, 700, f"Categoria: {card['category']}")

        # Descrição e status
        c.drawString(50, 680, f"Status: {card['status']}")
        c.drawString(50, 660, f"Descrição: {card.get('description', 'Sem descrição')}")

        # Tabela de acessórios e implementos (exemplo fictício)
        c.drawString(50, 630, "Acessórios e Implementos:")
        accessories = [
            ["Denominação", "Aplicação", "Características"],
            ["Placa Universal", "Fixação de Peça", "8''"],
            ["Luneta Fixa", "Usinagem de Peça", "10''"],
            ["Jogo de Engrenagens", "Abertura de Rosca", "40-128 Dentes"]
        ]

        table = Table(accessories, colWidths=[150, 200, 100])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        table.wrapOn(c, 50, 550)
        table.drawOn(c, 50, 550)

        # Histórico de manutenção
        c.drawString(50, 500, "Histórico de Manutenção Corretiva:")
        historico = [
            ["Data", "Ocorrência/Descrição", "Nº OS", "Visto"],
            ["05/10/2018", "Troca de correia do avanço do torno", "1023", "OK"],
            ["20/02/2023", "Lubrificação preventiva", "2025", "OK"]
        ]

        history_table = Table(historico, colWidths=[80, 300, 80, 50])
        history_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        history_table.wrapOn(c, 50, 350)
        history_table.drawOn(c, 50, 350)

        # Finalizar o PDF
        c.save()
        return send_file(pdf_path, as_attachment=True)
    
    except FileNotFoundError:
        return "Arquivo cards.json não encontrado", 404