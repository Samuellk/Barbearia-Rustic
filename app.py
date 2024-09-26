from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flask'

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
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = None
        cursor = None

        try:
            conn = conectar_banco()
            if conn is None:
                flash("Erro ao conectar ao banco de dados", "error")
                return redirect(url_for('login'))

            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM clientes WHERE nome = %s"
            cursor.execute(sql, (username,))
            cliente = cursor.fetchone()

            if cliente and check_password_hash(cliente['senha'], password):
                session['cliente_id'] = cliente['id_cliente']  
                session['cliente_nome'] = cliente['nome']
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('pagina_inicial'))
            else:
                flash("Nome de usuário ou senha incorretos!", "error")
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
    if 'cliente_id' not in session:
        flash("Você precisa estar logado para acessar esta página.", "error")
        return redirect(url_for('login'))

    return render_template('pagina_inicial.html', nome=session['cliente_nome'])

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

        conn = conectar_banco()
        if conn is None:
            flash("Erro ao conectar ao banco de dados.", "error")
            return redirect(url_for('agendamento'))

        cursor = conn.cursor()

        try:
            sql_agendamento = """
                INSERT INTO agendamentos (nome_cliente, contato_cliente, email_cliente, data, horario, servico, valor)
                VALUES (%s, %s, %s, STR_TO_DATE(%s, '%%d/%%m/%%Y'), %s, %s, %s)
            """
            val = (nome_cliente, contato_cliente, email_cliente, data, horario, servico, valor)

            cursor.execute(sql_agendamento, val)
            conn.commit()

            flash("Agendamento realizado com sucesso!", "success")

        except mysql.connector.Error as err:
            print(f"Erro ao realizar o agendamento: {err}")
            flash(f"Erro ao realizar o agendamento: {err}", "error")

        finally:
            if conn:
                cursor.close()
                conn.close()

        return redirect(url_for('agendamento'))

    return render_template('agendamento.html')

@app.route('/consulta_agendamentos', methods=['GET', 'POST'])
def consulta_agendamentos():
    if request.method == 'POST':
        nome_cliente = request.form.get('nome_cliente')

        if not nome_cliente:
            flash("Por favor, insira o nome do cliente.", "error")
            return redirect(url_for('consulta_agendamentos'))

        try:
            conn = mysql.connection
            cursor = conn.cursor()
            sql = '''
                SELECT a.servico, a.data_agendamento AS data, a.horario 
                FROM agendamentos a
                JOIN clientes c ON a.id_cliente = c.id_cliente
                WHERE c.nome = %s
            '''
            cursor.execute(sql, (nome_cliente,))
            agendamentos = cursor.fetchall()

        except Exception as e:
            flash(f"Ocorreu um erro: {str(e)}", "error")
            return redirect(url_for('consulta_agendamentos'))

        finally:
            cursor.close()

        return render_template('consulta_agendamentos.html', agendamentos=agendamentos, nome_cliente=nome_cliente)

    return render_template('consulta_agendamentos.html', agendamentos=None)


if __name__ == '__main__':
    app.run(debug=True)
