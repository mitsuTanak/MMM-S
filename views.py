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
    print("Acessando rota de cadastro")

    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        senha = request.form.get('password')
        role = request.form.get('role')

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
# Rota para criar os cards

# _________________________________________________________________________________________________
@app.route('/save_machine', methods=['POST'])
def save_machine():
    data = request.form
    image = request.files.get('image')  # Obter a imagem do formulário

    # Verifica se o arquivo de imagem existe e se tem uma extensão válida
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        image_url = f"/static/uploads/{image_filename}"  # Caminho para acessar a imagem no HTML
    else:
        image_url = None  # Se não houver imagem ou a extensão for inválida, define como None

    # Adicionar o campo de descrição
    description = data.get('card-description', None)  # Captura a descrição do formulário, se existir

    # Salvar as informações da máquina no banco de dados (tabela 'collection')
    cursor = mysql.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO collection (machine_name, model, manufacturing_year, price, sector, category, status, image_path, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (data['card-name'], data['card-model'], data['card-year'], data['card-price'], data['card-sector'], 
             data['card-category'], data['card-status'], image_url, description)
        )
        mysql.commit()

        # Recupera o ID gerado para o novo card (máquina)
        cursor.execute("SELECT LAST_INSERT_ID()")
        machine_id = cursor.fetchone()[0]

        # Retorna o ID e o caminho da imagem como resposta para o frontend
        response = {
            'id': machine_id,
            'image_url': image_url,
            'name': data['card-name']
        }

        return jsonify(response)  # Envia os dados como resposta JSON

    except Exception as e:
        mysql.rollback()
        flash(f'Erro ao cadastrar a máquina. Tente novamente. Detalhes do erro: {e}')  # Detalhes do erro
        print(f"Erro ao salvar no banco de dados: {e}")  # Detalhes no console
        return jsonify({'error': f'Erro ao salvar a máquina: {e}'}), 500  # Resposta detalhada no JSON
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