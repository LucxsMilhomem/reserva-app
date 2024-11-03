from conexao_bd import conexao_fechar, conexao_abrir
from datetime import datetime

def filtrar_reservas(con, usuario, sala):
    cursor = con.cursor(dictionary=True)
    sql = "SELECT reservas.Id, usuario.nome AS nome, reservas.Id_sala, salas.tipo AS sala, salas.descricao, reservas.horario_inicio AS inicio, reservas.horario_final AS final FROM reservas JOIN salas ON reservas.Id_sala = salas.Id JOIN usuario ON reservas.Id_usuario = usuario.Id WHERE (usuario.nome LIKE CONCAT('%', %s, '%') AND salas.tipo LIKE CONCAT('%', %s, '%') OR salas.descricao LIKE CONCAT('%', %s, '%'))"
    cursor.execute(sql, (usuario, sala, sala))
    reservas = cursor.fetchall()  
    
    for reserva in reservas:
        print(f"Reservas: {reserva['Id']} - Usuário: {reserva['nome']} - Sala: {reserva['sala']} - Descrição: {reserva['descricao']} - Início: {reserva['inicio']} - Fim: {reserva['final']}")

    cursor.close()
    return reservas

def inserir_reserva(con, Id_sala, Id_usuario, horario_inicio, horario_final):
    cursor = con.cursor()
    sql = "INSERT INTO reservas (Id_sala, Id_usuario, horario_inicio, horario_final) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (Id_sala, Id_usuario, horario_inicio, horario_final))
    con.commit()
    cursor.close()
    
def deletar_reserva(con, reserva_id):
    cursor = con.cursor()
    sql = "DELETE FROM reservas WHERE Id = %s"
    cursor.execute(sql, (reserva_id,))
    con.commit()
    cursor.close()

def listar_salas(con):
    cursor = con.cursor(dictionary=True)
    sqlcode = "SELECT * FROM salas"
    cursor.execute(sqlcode)
    lista_salas = cursor.fetchall()
    
    for sala in lista_salas:
        print(f"Salas: {sala['Id']} - Tipo: {sala['tipo']} - Capacidade: {sala['capacidade']} - Descrição: {sala['descricao']}")
    
    cursor.close()
    return lista_salas

def inserir_sala(con, tipo, capacidade, descricao, ativa):
    cursor = con.cursor()
    sql = "INSERT INTO salas (tipo, capacidade, descricao, ativa) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (tipo, capacidade, descricao, ativa))
    con.commit()
    cursor.close()

def listar_usuarios(con):
    cursor = con.cursor(dictionary=True)
    sqlcode = "SELECT * FROM usuario"
    cursor.execute(sqlcode)

    for usuario in cursor:
        print(f"Id: {usuario['Id']} - Nome: {usuario['nome']} - Email: {usuario['email']} - Senha: {usuario['senha']} ")
        
    cursor.close()
    
def inserir_usuario(con, nome, email, senha):
    cursor = con.cursor()
    sql = "INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)"
    cursor.execute(sql, (nome, email, senha))
    con.commit() 
    cursor.close()

def verificacao_conflito(con, sala, inicio, fim):
    if inicio > fim:
        return True
    reservas = filtrar_reservas(con, "", "")
    
    for reserva in reservas:
        if "Id_sala" in reserva and str(reserva["Id_sala"]) == str(sala):
            inicioReg = reserva["inicio"]
            fimReg = reserva["final"]

            if isinstance(inicioReg, str):
                inicioReg = datetime.fromisoformat(inicioReg)

            if isinstance(fimReg, str):
                fimReg = datetime.fromisoformat(fimReg)

            if not (fim <= inicioReg or inicio >= fimReg):
                return True
    return False


def verificar_login(con, email, senha):
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM usuario WHERE email = %s AND senha = %s"
    cursor.execute(sql, (email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    if usuario is not None:
        return True, usuario['Id'], usuario['nome']
    return False, None, None

def main():
    con = conexao_abrir("127.0.0.1", "root", "123456", "reserva")
    try:
        filtrar_reservas(con, "", "")
        listar_salas(con)
        listar_usuarios(con)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        conexao_fechar(con)

if __name__ == "__main__":
    main()
