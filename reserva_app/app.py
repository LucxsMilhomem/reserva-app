from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__, template_folder=os.path.abspath('templates'))

CSV_FILE_SALAS = 'cadastroSalas.csv'
CSV_FILE_RESERVAS = 'reservas.csv'

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/cadastrar_sala", methods=['GET', 'POST'])
def cadastrar_sala():
    if request.method == 'POST':
        tipo = request.form['tipo']
        capacidade = request.form['capacidade']
        descricao = request.form['descricao']

        file_exists = os.path.isfile(CSV_FILE_SALAS)
        
        with open(CSV_FILE_SALAS, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Tipo', 'Capacidade', 'Descrição'])
            writer.writerow([tipo, capacidade, descricao])
        
        return redirect("/listar_salas")
    return render_template("cadastrar-sala.html")

@app.route("/listar_salas")
def listar_salas():
    salas = []
    try:
        with open(CSV_FILE_SALAS, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                salas.append({
                    'tipo': row['Tipo'],
                    'capacidade': row['Capacidade'],
                    'descricao': row['Descrição']
                })
    except FileNotFoundError:
        print("Arquivo CSV não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o CSV: {e}")
    
    return render_template("listar-salas.html", salas=salas)



@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/reservar_sala", methods=['GET', 'POST'])
def reservar_sala():
    salas = []
    try:
        with open(CSV_FILE_SALAS, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                salas.append({
                    'tipo': row['Tipo'],
                    'capacidade': row['Capacidade'],
                    'descricao': row['Descrição']
                })
    except FileNotFoundError:
        print("Arquivo CSV não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o CSV: {e}")
    
    if request.method == 'POST':
        sala = request.form['sala']
        inicio = request.form['inicio']
        fim = request.form['fim']

        file_exists = os.path.isfile(CSV_FILE_RESERVAS)
        
        with open(CSV_FILE_RESERVAS, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Sala', 'Inicio', 'Fim'])
            writer.writerow([sala, inicio, fim])
        
        return redirect("/reservas")
    return render_template("reservar-sala.html", salas=salas)

@app.route("/reservas")
def reservas():
    reservas = []
    try:
        with open(CSV_FILE_RESERVAS, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                reservas.append(row)
    except FileNotFoundError:
        print("Arquivo CSV não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o CSV: {e}")

    return render_template("reservas.html", reservas=reservas)

@app.route("/reserva/detalhe_reserva")
def detalhe_reserva():
    return render_template("reserva/detalhe-reserva.html")

if __name__ == "__main__":
    app.run(debug=True)
