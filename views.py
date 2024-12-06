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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Rotas
# @app.route("/cadastrar_manutencao") 
# def solucionar():
#     return render_template("solucionar.html")

@app.route("/politica") 
def politica():
    return render_template("politica.html")

@app.route("/termos") 
def termos():
    return render_template("termos.html")

@app.route("/home") 
def home():
    return render_template("home.html")

@app.route("/detalhes") 
def detalhes():
    return render_template("detalhes.html")

@app.route("/visitante") 
def visitante():
    return render_template("visitante.html")

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
                return redirect(url_for('visitante'))

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

# Manutenção
# Rota para o cadastro de manutenção
@app.route('/cadastrar_manutencao', methods=['GET', 'POST'])
def save_maintenance():
    if request.method == 'POST':
        data = request.form
        required_fields = ['problem_description', 'solution', 'cost']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            flash(f'Erro: Campos obrigatórios ausentes: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('save_maintenance'))

        anomaly_image = request.files.get('anomaly_image')
        solution_image = request.files.get('solution_image')
        anomaly_image_url, solution_image_url = None, None

        if anomaly_image and allowed_file(anomaly_image.filename):
            try:
                anomaly_image_filename = secure_filename(anomaly_image.filename)
                anomaly_image_path = os.path.join(app.config['UPLOAD_FOLDER'], anomaly_image_filename)
                anomaly_image.save(anomaly_image_path)
                anomaly_image_url = f"/static/uploads/{anomaly_image_filename}"
            except Exception as e:
                flash(f'Erro ao salvar imagem da anomalia: {str(e)}', 'error')
                return redirect(url_for('save_maintenance'))

        if solution_image and allowed_file(solution_image.filename):
            try:
                solution_image_filename = secure_filename(solution_image.filename)
                solution_image_path = os.path.join(app.config['UPLOAD_FOLDER'], solution_image_filename)
                solution_image.save(solution_image_path)
                solution_image_url = f"/static/uploads/{solution_image_filename}"
            except Exception as e:
                flash(f'Erro ao salvar imagem da solução: {str(e)}', 'error')
                return redirect(url_for('save_maintenance'))

        cursor = mysql.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO maintenance (problem_description, anomaly_image, solution, cost, sector, category, solution_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data['problem_description'],
                    anomaly_image_url,
                    data['solution'],
                    data['cost'],
                    data['sector'],
                    data['category'],
                    solution_image_url,
                )
            )
            mysql.commit()
            flash('Registro de manutenção criado com sucesso!', 'success')
            return redirect(url_for('save_maintenance'))

        except Exception as e:
            mysql.rollback()
            flash(f'Erro ao inserir no banco de dados: {str(e)}', 'error')
            return redirect(url_for('save_maintenance'))

        finally:
            cursor.close()

    return render_template("solucionar.html")




# Card
# _________________________________________________________________________________________________
@app.route('/save_machine', methods=['POST'])
def save_machine():
    data = request.form
    image = request.files.get('image')  # Obter a imagem
    pdf = request.files.get('pdf')  # Obter o PDF

    # Salvar a imagem
    image_url = None
    if image and allowed_file(image.filename):  # Verifica a imagem
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        image_url = f"/static/uploads/{image_filename}"  # Caminho acessível no HTML

   # Salvar o PDF
    pdf_url = None
    if pdf and allowed_file(pdf.filename, allowed_extensions={'pdf'}):  # Verifica o PDF
        pdf_filename = secure_filename(pdf.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    try:
        pdf.save(pdf_path)  # Salva o arquivo PDF no diretório de uploads
        pdf_url = f"/static/uploads/{pdf_filename}"  # Caminho acessível no HTML
    except Exception as e:
        print(f"Erro ao salvar o arquivo PDF: {e}")  # Log do erro

    # Salvar no banco de dados (adicionando o campo PDF)
    cursor = mysql.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO collection (machine_name, model, manufacturing_year, price, sector, category, status, description, image_path, pdf_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (data['card-name'], data['card-model'], data['card-year'], data['card-price'],
            data['card-sector'], data['card-category'], data['card-status'],
            data.get('card-description'), image_url, pdf_url)  # AQUI, pdf_url sendo passado corretamente
        )
        mysql.commit()

        machine_id = cursor.lastrowid
        response = {
            'id': machine_id,
            'image_url': image_url,
            'pdf_url': pdf_url,  # Incluir a URL do PDF
            'name': data['card-name']
        }
        return jsonify(response)
    except Exception as e:
        mysql.rollback()
        print(f"Erro ao salvar no banco: {e}")
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
            # Gerar o caminho correto para o PDF
            if machine['pdf_path']:
                machine['pdf_url'] = url_for('static', filename=f'upload/{machine["pdf_path"]}')
            else:
                machine['pdf_url'] = None  # Caso não tenha PDF

            # Passa o papel do usuário para o template
            return render_template('detalhamento.html', card=machine, user_role=getattr(current_user, 'role', 'visitor'))
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

        if not card:
            return "Card não encontrado", 404

        # Converter o status para valores esperados
        status_mapping = {
            'operating': 'Operando',
            'stopped': 'Parado',
            'waiting': 'Aguardando Manutenção'
        }
        card['status'] = status_mapping.get(card['status'], 'Indefinido')

        # Calcular o custo total por setor
        cursor.execute("""
            SELECT sector, SUM(price) as total_cost
            FROM collection
            GROUP BY sector
        """)
        sector_costs = cursor.fetchall()

        # Transformar os dados em JSON antes de passar para o template
        sector_costs_json = json.dumps(sector_costs)

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
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 770, "FICHA DE MÁQUINAS E EQUIPAMENTOS")

        # Desenhando a linha
        c.line(50, 765, 550, 765)

        # Tabela com informações da máquina/equipamento
        data = [
            ["Máquina ou Equipamento", f"{card['name']} | {card['model']}"],
            ["NI", f"{card['year']}", "Ano de Fabricação", f"{card['year']}"],
            ["Setor", f"{card['sector']}"]
        ]
        
        table = Table(data, colWidths=[200, 200, 150, 150])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        table.wrapOn(c, 50, 700)
        table.drawOn(c, 50, 700)

        # Adicionando título para o histórico de manutenção
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 620, "Histórico de Manutenção")
        
        # Linha do título do histórico
        c.line(50, 615, 550, 615)

        # Tabela de histórico de manutenção
        historico = [
            ["Data", "Ocorrência/Descrição", "Ordem", "Visto"],
            ["06/12/2024", "Verificação de segurança e otimização do desempenho", "N/A", "OK"],
            ["17/11/2024", "Substituição do equipamento defeituoso e reconfiguração da rede", "N/A", "OK"],
            ["25/10/2024", "Revisão do código-fonte, aplicação de patches e testes para corrigir falhas", "N/A", "OK"]
        ]
        
        history_table = Table(historico, colWidths=[100, 300, 80, 50])
        history_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        history_table.wrapOn(c, 50, 400)
        history_table.drawOn(c, 50, 400)

        # Finalizar o PDF
        c.save()
        return send_file(pdf_path, as_attachment=True)
    
    except FileNotFoundError:
        return "Arquivo cards.json não encontrado", 404



# Gráfico
# Importa os dados do custo de manutenção
@app.route('/api/maintenance-costs')
def get_maintenance_costs():
    cursor = mysql.cursor(dictionary=True)  # Usa dictionary=True para mapear resultados em dict diretamente
    try:
        query = """
            SELECT sector, SUM(cost) AS total_cost
            FROM maintenance 
            GROUP BY sector
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results)  # Retorna diretamente a lista de dicionários

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()

