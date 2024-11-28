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
        confirm_senha = request.form['confirm_password']

        # Verifica se as senhas coincidem
        if senha != confirm_senha:
            flash('As senhas não coincidem.')
            return redirect('/cadastro')

        # Gera um hash da senha para armazenamento seguro
        senha_hash = generate_password_hash(senha)

        # Conecta ao banco de dados usando a nova função
        conn = conectar_banco()
        if conn is None:
            flash('Erro ao conectar ao banco de dados.')
            return redirect('/cadastro')

        cursor = conn.cursor()

        # Verifica o tipo de usuário pelo domínio do email
        if email.endswith('@gmail.com'):
            tabela = 'clientes'
        elif email.endswith('@barbeiro.com'):
            tabela = 'funcionarios'
        elif email.endswith('@admin.com'):
            tabela = 'administradores'
        else:
            flash('Domínio de email inválido.')
            return redirect('/cadastro')

        # Insere o cadastro na tabela correspondente
        try:
            cursor.execute(f"""
                INSERT INTO {tabela} (nome, email, contato, senha) 
                VALUES (%s, %s, %s, %s)
            """, (nome, email, contato, senha_hash))
            conn.commit()
            flash('Cadastro realizado com sucesso!')
            return redirect('/login')
        except mysql.connector.Error as err:
            flash(f'Erro ao cadastrar: {err}')
            return redirect('/cadastro')
        finally:
            cursor.close()
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
        senha_cliente = request.form.get('senha_cliente')
        contato_cliente = request.form.get('contato_cliente')
        email_cliente = request.form.get('email_cliente')
        barbeiro_selecionado = request.form.get('Barbeiro_selecionado')
        data = request.form.get('data')  
        horario = request.form.get('horario')  
        servico = request.form.get('servico')
        valor = request.form.get('valor')

        print(f"Dados recebidos: Nome: {nome_cliente}, Senha: {senha_cliente}, Contato: {contato_cliente}, "
              f"Email: {email_cliente}, Barbeiro: {barbeiro_selecionado}, Data: {data}, Horário: {horario}, "
              f"Serviço: {servico}, Valor: {valor}")

        try:
            from datetime import datetime
            data_formatada = datetime.strptime(data, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError as ve:
            print(f"Erro na formatação da data: {ve}")
            flash("Data inválida. Use o formato MM/DD/YYYY.", "error")
            return redirect(url_for('agendamento'))

        try:
            valor_formatado = float(valor)
        except ValueError as ve:
            print(f"Erro ao formatar o valor: {ve}")
            flash("Valor inválido.", "error")
            return redirect(url_for('agendamento'))
        
        conn = conectar_banco()
        if conn is None:
            flash("Erro ao conectar ao banco de dados.", "error")
            return redirect(url_for('agendamento'))

        cursor = conn.cursor()
        try:
            
            from werkzeug.security import generate_password_hash
            senha_hash = generate_password_hash(senha_cliente)

            sql = """
                INSERT INTO agendamentos (
                    nome_cliente, senha_cliente, contato_cliente, email_cliente,
                    barbeiro_selecionado, data, horario, servico, valor
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (nome_cliente, senha_hash, contato_cliente, email_cliente,
                       barbeiro_selecionado, data_formatada, horario, servico, valor_formatado)
            cursor.execute(sql, valores)
            conn.commit()

            flash("Agendamento realizado com sucesso!", "success")
        except mysql.connector.Error as err:
            print(f"Erro ao salvar o agendamento no banco de dados: {err}")
            flash(f"Erro ao salvar o agendamento: {err}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('pagina_inicial'))
    
    barbeiro = request.args.get('barbeiro')
    servico = request.args.get('servico')
    valor = request.args.get('valor')

    return render_template('agendamento.html', barbeiro=barbeiro, servico=servico, valor=valor)

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
            sql = "SELECT id, servico, data, barbeiro_selecionado, horario FROM agendamentos WHERE nome_cliente = %s"
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
        barbeiro_selecionado = request.form['barbeiro']
        servico = request.form['servico']
        valor = request.form['valor']

        valor_decimal = float(valor.replace('R$ ', '').replace(',', '.'))

        cursor.execute('''
            UPDATE agendamentos
            SET nome_cliente = %s, contato_cliente = %s, email_cliente = %s,
                data = %s, horario = %s, barbeiro_selecionado = %s, servico = %s, valor = %s
            WHERE id = %s
        ''', (nome_cliente, contato_cliente, email_cliente, data, horario, barbeiro_selecionado, servico, valor_decimal, agendamento_id))

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

@app.route('/meus_agendamentos')
def meus_agendamentos():
    if 'user_id' not in session or session['user_tipo'] != 'funcionarios':
        flash('Você não está logado como barbeiro.', 'error')
        return redirect(url_for('login'))  # Redireciona para a página de login

    barbeiro_id = session['user_id']

    # Conecte-se ao banco de dados e busque os agendamentos do barbeiro
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM agendamentos WHERE barbeiro = %s", (barbeiro_id,))
        agendamentos = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Erro ao acessar os agendamentos: {err}', 'error')
        return redirect(url_for('login'))
    finally:
        cursor.close()
        conn.close()

    return render_template('meus_agendamentos.html', agendamentos=agendamentos)

@app.route('/barbeiros')
def barbeiros():
    # Verifica se o usuário está logado e é um barbeiro
    if 'user_id' not in session or session['user_tipo'] != 'funcionarios':
        flash('Você não está logado como barbeiro.', 'error')
        return redirect(url_for('login'))  # Redireciona para a página de login

    barbeiro_nome = session['user_nome']  # Nome do barbeiro que está logado
    
    # Conecte-se ao banco de dados e busque os agendamentos
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscando agendamentos do barbeiro
        cursor.execute("SELECT * FROM agendamentos WHERE barbeiro = %s", (barbeiro_nome,))
        agendamentos = cursor.fetchall()
        
        # Buscando o cronograma do barbeiro
        cursor.execute("SELECT * FROM cronograma WHERE barbeiro = %s", (barbeiro_nome,))
        cronograma = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Erro ao acessar os dados: {err}', 'error')
        return redirect(url_for('login'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('barbeiro_dashboard.html', barbeiro_nome=barbeiro_nome, agendamentos=agendamentos, cronograma=cronograma)

@app.route('/horarios_disponiveis/<barbeiro_id>/<data_selecionada>')
def horarios_disponiveis(barbeiro_id, data_selecionada):
    conn = conectar_banco()
    if conn is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'})

    cursor = conn.cursor()
    data_formatada = datetime.strptime(data_selecionada, '%d/%m/%Y')
    dia_semana = data_formatada.weekday()

    horarios_ter_sex = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00']

    horarios_sab = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30']

    if dia_semana >= 1 and dia_semana <= 4:
        horarios_disponiveis = horarios_ter_sex
    elif dia_semana == 5:
        horarios_disponiveis = horarios_sab
    else:
        horarios_disponiveis = []

    cursor.execute("""
        SELECT horario FROM cronograma 
        WHERE barbeiro_id = %s AND data = %s AND status = 'disponivel'
    """, (barbeiro_id, data_selecionada))

    horarios_ocupados = cursor.fetchall()
    horarios_ocupados = [h[0] for h in horarios_ocupados]

    horarios_final = [h for h in horarios_disponiveis if h not in horarios_ocupados]

    cursor.close()
    conn.close()

    return jsonify({'horarios': horarios_final})

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    session.clear() 
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))
   
@app.route('/funcionario', methods=['GET'])
def funcionario():
    
    servico = request.args.get('servico')   
    valor = request.args.get('valor')       

    barbeiros = [
        {"nome": "João Silva", "foto": "barbeiro1.jpg"},
        {"nome": "Carlos Pereira", "foto": "barbeiro2.jpg"},
        {"nome": "Lucas Oliveira", "foto": "barbeiro3.jpg"},
        {"nome": "Rafael Santos", "foto": "barbeiro4.jpg"},
        {"nome": "André Almeida", "foto": "barbeiro5.jpg"},
        {"nome": "Gabriel Pires", "foto": "barbeiro6.jpg"},
    ]

    return render_template('funcionario.html', barbeiros=barbeiros, servico=servico, valor=valor)
   

@app.route('/mensagem/<int:cliente_id>/<int:barbeiro_id>', methods=['GET', 'POST'])
def mensagem(cliente_id, barbeiro_id):
    conn = conectar_banco()
    if not conn:
        return "Erro ao conectar ao banco de dados", 500

    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        if conteudo:
            try:
                query = "INSERT INTO mensagem (cliente_id, barbeiro_id, conteudo, remetente) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (cliente_id, barbeiro_id, conteudo, 'cliente'))
                conn.commit()
            except mysql.connector.Error as err:
                return f"Erro ao salvar mensagem: {err}", 500

    try:
        query = """
            SELECT * FROM mensagem
            WHERE (cliente_id = %s AND barbeiro_id = %s)
            ORDER BY data_envio ASC
        """
        cursor.execute(query, (cliente_id, barbeiro_id))
        mensagem = cursor.fetchall()
    except mysql.connector.Error as err:
        return f"Erro ao buscar mensagem: {err}", 500
    finally:
        conn.close()

    return render_template('mensagem.html', mensagem=mensagem, cliente_id=cliente_id, barbeiro_id=barbeiro_id)


if __name__ == '__main__':
    app.run(debug=True)