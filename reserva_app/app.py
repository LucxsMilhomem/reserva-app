from flask import Flask, render_template, request, redirect, g, session, url_for
from funcoes_bd import *
from conexao_bd import conexao_fechar, conexao_abrir
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

def get_db_connection():
    if 'con' not in g:
        g.con = conexao_abrir("127.0.0.1", "root", "123456", "reserva")
    return g.con

@app.teardown_appcontext
def teardown_db_connection(exception):
    con = g.pop('con', None)
    if con is not None:
        conexao_fechar(con)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("password")

        con = get_db_connection()
        logado, id_usuario, nome_usuario = verificar_login(con, email, senha)
        if logado:
            session['idUsuario'] = id_usuario
            session['usuarioF'] = nome_usuario
            return redirect("/reservas")
        return render_template("login.html", erro="Login Incompatível")
    return render_template("login.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "POST":
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('password')
        
        con = get_db_connection()
        verif, erro = verificar_cadastro(con, nome, email)
        
        if verif:
            return render_template("cadastro.html", erro=erro)
        
        inserir_usuario(con, nome, email, senha)
        
        logado, id_usuario, nome_usuario = verificar_login(con, email, senha)
        if logado:
            session['idUsuario'] = id_usuario
            session['usuarioF'] = nome_usuario
        return redirect("/reservas")

    return render_template("cadastro.html")

@app.route("/cadastrar_sala", methods=['GET', 'POST'])
def cadastrar_sala():
    if request.method == 'POST':
        tipo = request.form['tipo']
        capacidade = request.form['capacidade']
        descricao = request.form['descricao']
        ativa = True
        con = get_db_connection()
        inserir_sala(con, tipo, capacidade, descricao, ativa)
        return redirect("/listar_salas")
    return render_template("cadastrar-sala.html")

@app.route("/listar_salas")
def listar_salas_form():
    con = get_db_connection()
    salas = listar_salas(con)
    return render_template("listar-salas.html", salas=salas)

@app.route("/editar_sala/<int:sala_id>", methods=["GET", "POST"])
def editar_sala(sala_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('SELECT * FROM salas WHERE Id = %s', (sala_id,))
    sala = cursor.fetchone()

    if request.method == "POST":
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        capacidade = request.form['capacidade']
        cursor.execute('UPDATE salas SET tipo = %s, descricao = %s, capacidade = %s WHERE Id = %s',
                       (tipo, descricao, capacidade, sala_id))
        con.commit()
        cursor.close()
        return redirect(url_for('listar_salas_form'))
    return render_template("editar-sala.html", sala=sala)



@app.route("/alterar_status_sala/<int:sala_id>")
def alterar_status_sala(sala_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute('SELECT * FROM salas WHERE id = %s', (sala_id,))
    sala = cursor.fetchone()

    if sala is None:
        cursor.close()
        return redirect('/listar_salas')

    nova_atividade = not sala['ativa']
    cursor.execute('UPDATE salas SET ativa = %s WHERE id = %s', (nova_atividade, sala_id))
    con.commit()
    cursor.close()

    return redirect('/listar_salas')


@app.route("/excluir_sala/<int:sala_id>")
def excluir_sala(sala_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('DELETE FROM salas WHERE id = %s', (sala_id,))
    con.commit()
    cursor.close()
    return redirect("/listar_salas")


@app.route("/reservar_sala", methods=["GET", "POST"])
def reservar_sala():
    con = get_db_connection()

    salas = listar_salas(con)
    salas_ativas = [sala for sala in salas if sala.get('ativa') == 1]
    
    if request.method == "POST":
        idUsuario = session.get('idUsuario')
        sala_id = request.form['sala']
        inicio = request.form['inicio']
        fim = request.form['fim']

        horainicio = datetime.fromisoformat(inicio)
        horafim = datetime.fromisoformat(fim)

        if verificacao_conflito(con, sala_id, horainicio, horafim):
            return render_template("reservar-sala.html", salas=salas_ativas, erro="Reserva Indisponível")
        
        inserir_reserva(con, sala_id, idUsuario, inicio, fim)
        
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT Id FROM reservas WHERE Id_sala = %s AND Id_usuario = %s AND horario_inicio = %s AND horario_final = %s", (sala_id, idUsuario, inicio, fim))
        reserva_Id = cursor.fetchone()
        
        session['reserva_id'] = reserva_Id['Id']
        print(session['reserva_id'])
        
        print(reserva_Id)
        
        return redirect("/detalhe_reserva")

    return render_template("reservar-sala.html", salas=salas_ativas)

@app.route("/reservas", methods=["GET"])
def reservas():
    sala_filtro = request.args.get('sala', "")  
    nome_filtro = request.args.get('usuario', "")   
    con = get_db_connection()
    reservas = filtrar_reservas(con, nome_filtro, sala_filtro)
    return render_template("reservas.html", reservas=reservas)

@app.route("/minhas_reservas")
def minhas_reservas():
    con = get_db_connection()
    idUsuario = session.get('usuarioF')
    reservas = filtrar_reservas(con, idUsuario, "")

    return render_template("minhas-reservas.html", reservas=reservas)

@app.route("/detalhe_reserva", methods=["GET", "POST"])
def detalhe_reserva():
    if request.method == "POST":
        reserva_id = request.form.get('reserva_id')
        session['reserva_id'] = reserva_id
        return redirect("/detalhe_reserva")
    
    print(session['reserva_id'])

    reserva_id = session.get('reserva_id')
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""SELECT usuario.nome AS usuario,
                      reservas.Id, 
                      salas.tipo AS sala, 
                      salas.descricao, 
                      reservas.horario_inicio AS inicio, 
                      reservas.horario_final AS final 
                      FROM reservas 
                      JOIN salas ON reservas.Id_sala = salas.Id 
                      JOIN usuario ON reservas.Id_usuario = usuario.Id 
                      WHERE reservas.Id = %s""", (reserva_id,))
    reserva = cursor.fetchone()

    if reserva:
        if isinstance(reserva['inicio'], str):
            inicio = datetime.fromisoformat(reserva['inicio'])
        else:
            inicio = reserva['inicio']

        if isinstance(reserva['final'], str):
            fim = datetime.fromisoformat(reserva['final'])
        else:
            fim = reserva['final']

        reserva['inicio'] = inicio.strftime('%d/%m/%Y %H:%M')
        reserva['final'] = fim.strftime('%d/%m/%Y %H:%M')

    cursor.close()
    return render_template("detalhe-reserva.html", reserva=reserva)

@app.route("/cancelar_reserva", methods=["POST"])
def cancelar_reserva():
    con = get_db_connection()
    reserva_id = request.form.get('reserva_id')

    if reserva_id:
        deletar_reserva(con, reserva_id)  
        session.pop('detalhes_reserva', None)  
    return redirect("/reservas")

if __name__ == "__main__":
    app.run(debug=True)
