from flask import Flask, render_template, request, redirect, g, session
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

@app.route("/reservar_sala", methods=["GET", "POST"])
def reservar_sala():
    con = get_db_connection()

    salas = listar_salas(con)
    salas_ativas = [sala for sala in salas if sala.get('ativa') == 1]
    
    if request.method == "POST":
        idUsuario = session.get('idUsuario')
        sala = request.form['sala']
        inicio = request.form['inicio']
        fim = request.form['fim']

        horainicio = datetime.fromisoformat(inicio)
        horafim = datetime.fromisoformat(fim)

        if verificacao_conflito(con, sala, horainicio, horafim):
            return render_template("reservar-sala.html", salas=salas_ativas, erro="Reserva Indisponível")

        inserir_reserva(con, sala, idUsuario, inicio, fim)
        return redirect("/reservas")

    return render_template("reservar-sala.html", salas=salas_ativas)

@app.route("/reservas", methods=["GET"])
def reservas():
    sala_filtro = request.args.get("sala", "")  
    nome_filtro = request.args.get("usuario", "")   
    con = get_db_connection()
    reservas = filtrar_reservas(con, nome_filtro, sala_filtro)
    return render_template("reservas.html", reservas=reservas)

@app.route("/detalhe_reserva")
def detalhe_reserva():
    sala = request.args.get('sala')
    usuarioRes = request.args.get('usuario')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    iniDT = datetime.fromisoformat(inicio)
    fimDT = datetime.fromisoformat(fim)
    inicioDef = iniDT.strftime('%d/%m/%Y %H:%M')
    fimDef = fimDT.strftime('%d/%m/%Y %H:%M')
    return render_template("detalhe-reserva.html", sala=sala, usuario=usuarioRes, inicio=inicioDef, fim=fimDef)

if __name__ == "__main__":
    app.run(debug=True)