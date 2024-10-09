from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flask'
app.secret_key = 'sua_chave_secreta'

def conectar_banco():
    try:
        conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='admin123',  
            database='barbearia' 
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        contato = request.form['contact']
        senha = request.form['password']
        confirmar_senha = request.form['confirm_password']

        if senha != confirmar_senha:
            flash("As senhas não coincidem!", "error")
            return redirect(url_for('cadastro'))
        senha_hash = generate_password_hash(senha)

        conn = None
        cursor = None

        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            sql = "INSERT INTO clientes (nome, email, contato, senha) VALUES (%s, %s, %s, %s)"
            valores = (nome, email, contato, senha_hash)
            cursor.execute(sql, valores)
            conn.commit()

            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Erro ao realizar o cadastro: {str(e)}", "error")
            return redirect(url_for('cadastro'))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = None
        cursor = None

        try:
            conn = conectar_banco()
            if conn is None:
                flash("Erro ao conectar ao banco de dados", "error")
                return redirect(url_for('login'))

            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM clientes WHERE email = %s"
            cursor.execute(sql, (email,))
            cliente = cursor.fetchone()

            if cliente and check_password_hash(cliente['senha'], password):
                session['cliente_id'] = cliente['id_cliente'] 
                session['cliente_nome'] = cliente['nome']
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('pagina_inicial'))
            else:
                flash("Email ou senha incorretos!", "error")
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Erro ao fazer login: {str(e)}", "error")
            return redirect(url_for('login'))

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
    return render_template('login.html')


@app.route('/')
def home():
    return redirect(url_for('pagina_inicial'))

@app.route('/pagina_inicial')
def pagina_inicial():
    if 'cliente_nome' in session:
        return render_template('pagina_inicial.html', nome=session['cliente_nome'])
    else:
        flash("Erro: Nome do cliente não está na sessão.", "error")
    return redirect(url_for('login'))


@app.route('/satisfacao')
def satisfacao():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, comentario, nivel_satisfacao FROM feedbacks")
    feedbacks = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('satisfacao.html', feedbacks=feedbacks)

@app.route('/publicar_satisfacao', methods=['POST'])
def publicar_satisfacao():
    nome = request.form['nome']
    comentario = request.form['comentario']
    nivel_satisfacao = request.form['rating']
    
    conn = conectar_banco()
    cursor = conn.cursor()
    sql = "INSERT INTO feedbacks (nome, comentario, nivel_satisfacao) VALUES (%s, %s, %s)"
    val = (nome, comentario, nivel_satisfacao)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'nome': nome,
        'comentario': comentario,
        'nivel_satisfacao': nivel_satisfacao
    })

@app.route('/servicos')
def servicos():
    return render_template('servicos.html')

def validar_login(nome, contato, senha):
    
    if nome == "cliente_exemplo" and contato == "123456" and senha == "senha123":
        return type('Cliente', (object,), {"id": 1, "nome": nome})()
    return None

@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if request.method == 'POST':
        nome_cliente = request.form.get('nome_cliente')
        contato_cliente = request.form.get('contato_cliente')
        email_cliente = request.form.get('email_cliente')
        data = request.form.get('data')
        horario = request.form.get('horario')
        servico = request.form.get('servico')
        valor = request.form.get('valor')

        if not (nome_cliente and contato_cliente and email_cliente and data and horario and servico and valor):
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for('agendamento'))

        try:
            data_convertida = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            flash("Formato de data inválido. Use DD/MM/AAAA.", "error")
            return redirect(url_for('agendamento'))

        conn = conectar_banco()
        if conn is None:
            flash("Erro ao conectar ao banco de dados.", "error")
            return redirect(url_for('agendamento'))

        cursor = conn.cursor()

        try:
            sql_agendamento = """
                INSERT INTO agendamentos (nome_cliente, contato_cliente, email_cliente, data, horario, servico, valor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            valores = (nome_cliente, contato_cliente, email_cliente, data_convertida, horario, servico, valor)

            cursor.execute(sql_agendamento, valores)
            conn.commit()

            flash("Agendamento realizado com sucesso!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao realizar o agendamento: {err}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('pagina_inicial'))

    return render_template('agendamento.html')


@app.route('/consultar_agendamentos', methods=['GET', 'POST'])
def consultar_agendamentos():
    agendamentos = None
    nome_cliente = ""

    if request.method == 'POST':
        nome_cliente = request.form.get('nome_cliente')

        conn = conectar_banco()
        if conn is None:
            flash("Erro ao conectar ao banco de dados.", "error")
            return redirect(url_for('consultar_agendamentos'))

        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT id, servico, data, horario FROM agendamentos WHERE nome_cliente = %s"
            cursor.execute(sql, (nome_cliente,))
            agendamentos = cursor.fetchall()

            if not agendamentos:
                agendamentos = None

        except mysql.connector.Error as err:
            print(f"Erro ao consultar agendamentos: {err}")
            flash(f"Erro ao consultar agendamentos: {err}", "error")
            agendamentos = None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('consultar_agendamentos.html', agendamentos=agendamentos, nome_cliente=nome_cliente)

@app.route('/cancelar_agendamento/<int:agendamento_id>', methods=['POST'])
def cancelar_agendamento(agendamento_id):
    conn = conectar_banco()
    if conn is None:
        flash("Erro ao conectar ao banco de dados.", "error")
        return redirect(url_for('consultar_agendamentos'))

    cursor = conn.cursor()

    try:
        sql_cancelar = "DELETE FROM agendamentos WHERE id = %s"
        cursor.execute(sql_cancelar, (agendamento_id,))
        conn.commit()

        flash("Agendamento cancelado com sucesso!", "success")

    except mysql.connector.Error as err:
        print(f"Erro ao cancelar o agendamento: {err}")
        flash(f"Erro ao cancelar o agendamento: {err}", "error")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('consultar_agendamentos'))

@app.route('/alterar_agendamento/<int:agendamento_id>', methods=['GET', 'POST'])
def alterar_agendamento(agendamento_id):
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        contato_cliente = request.form['contato_cliente']
        email_cliente = request.form['email_cliente']
        data = request.form['data']
        horario = request.form['horario']
        servico = request.form['servico']
        valor = request.form['valor']

        valor_decimal = float(valor.replace('R$ ', '').replace(',', '.'))

        cursor.execute('''
            UPDATE agendamentos
            SET nome_cliente = %s, contato_cliente = %s, email_cliente = %s,
                data = %s, horario = %s, servico = %s, valor = %s
            WHERE id = %s
        ''', (nome_cliente, contato_cliente, email_cliente, data, horario, servico, valor_decimal, agendamento_id))

        conn.commit() 
        cursor.close()
        conn.close()

        flash('Agendamento alterado com sucesso!', 'success')
        return redirect(url_for('pagina_inicial')) 

    cursor.execute('SELECT * FROM agendamentos WHERE id = %s', (agendamento_id,))
    agendamento = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('alterar_agendamento.html', agendamento=agendamento)
   

if __name__ == '__main__':
    app.run(debug=True)