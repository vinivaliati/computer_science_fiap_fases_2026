"""
dados.py - banco de dados (SQLite) e carga do CSV da Aurora Siger.
Cria o banco, carrega o CSV, consulta e faz o CRUD completo (cadastrar, listar, alterar, excluir).
"""
import csv
import os
import sqlite3

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raiz do projeto
CAMINHO_BANCO = os.path.join(PASTA, "aurora_siger.db")
CAMINHO_SQL = os.path.join(PASTA, "script_banco.sql")
CAMINHO_CSV = os.path.join(PASTA, "dados_aurora_siger.csv")

COLUNAS = ["codigo_modulo", "modulo", "tipo", "ciclo", "consumo_kwh", "geracao_kwh",
           "bateria_pct", "temperatura_c", "ocupacao_pct", "status",
           "prioridade_alerta", "mensagem"]


def criar_banco():
    """Cria a tabela lendo o script_banco.sql. Devolve True se deu certo."""
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        with open(CAMINHO_SQL, encoding="utf-8") as arquivo:
            conexao.executescript(arquivo.read())
    except FileNotFoundError:
        print("Erro: script_banco.sql não encontrado.")
        return False
    except sqlite3.Error as erro:
        print("Erro no banco de dados:", erro)
        return False
    else:
        return True
    finally:
        if conexao:
            conexao.close()  # sempre fecha a conexão, deu erro ou não


def carregar_csv():
    """Lê o CSV e insere no banco. Linhas inválidas ou repetidas são puladas.
    Devolve (inseridos, ignorados)."""
    inseridos, ignorados = 0, 0
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        sql = "INSERT INTO registros (%s) VALUES (%s)" % (
            ", ".join(COLUNAS), ", ".join("?" * len(COLUNAS)))
        with open(CAMINHO_CSV, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                try:
                    valores = [linha[c].strip() for c in COLUNAS]
                    conexao.execute(sql, valores)
                    inseridos += 1
                except (sqlite3.IntegrityError, KeyError):
                    ignorados += 1  
        conexao.commit()
    except FileNotFoundError:
        print("Erro: dados_aurora_siger.csv não encontrado.")
    except sqlite3.Error as erro:
        print("Erro no banco de dados:", erro)
    finally:
        if conexao:
            conexao.close()
    return inseridos, ignorados


def consultar(filtro="", parametros=()):
    """Devolve lista de linhas (sqlite3.Row). Ex.: consultar('WHERE status = ?', ('alerta',))"""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    try:
        return conexao.execute("SELECT * FROM registros %s ORDER BY ciclo, codigo_modulo" % filtro,
                               parametros).fetchall()
    except sqlite3.Error as erro:
        print("Erro na consulta:", erro)
        return []
    finally:
        conexao.close()


def preparar():
    """Cria o banco e carrega o CSV só se a tabela estiver vazia."""
    if criar_banco() and not consultar():
        inseridos, ignorados = carregar_csv()
        print("CSV carregado: %d inseridos, %d ignorados." % (inseridos, ignorados))


# ===========================================================================
# CRUD (etapa 2): cadastrar, listar, alterar, excluir
# ===========================================================================
STATUS_VALIDOS = ("ativo", "manutenção", "alerta")
CAMPOS_TEXTO = ["codigo_modulo", "modulo", "tipo", "status", "mensagem"]
CAMPOS_INTEIROS = ["ciclo", "prioridade_alerta"]
CAMPOS_DECIMAIS = ["consumo_kwh", "geracao_kwh", "bateria_pct", "temperatura_c", "ocupacao_pct"]


# estruturas.py troca isto por uma função que empilha no histórico
ao_registrar = lambda texto: None


def executar_escrita(sql, parametros):
    """Roda INSERT/UPDATE/DELETE. Devolve (ok, mensagem, linhas_afetadas)."""
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
    except sqlite3.IntegrityError as erro:
        # CHECK ou UNIQUE do script_banco.sql barrou o dado
        return False, "Dado recusado pelo banco: %s" % erro, 0
    except sqlite3.Error as erro:
        return False, "Erro no banco de dados: %s" % erro, 0
    else:
        return True, "Operação realizada.", cursor.rowcount
    finally:
        if conexao:
            conexao.close()


def cadastrar(registro):
    """CREATE: recebe um dicionário com todas as colunas."""
    sql = "INSERT INTO registros (%s) VALUES (%s)" % (
        ", ".join(COLUNAS), ", ".join("?" * len(COLUNAS)))
    return executar_escrita(sql, [registro[c] for c in COLUNAS])


def alterar(id_registro, campo, valor):
    """UPDATE de um campo. O nome do campo vem de uma lista fixa (evita SQL injection)."""
    if campo not in COLUNAS:
        return False, "Campo inexistente.", 0
    ok, msg, n = executar_escrita("UPDATE registros SET %s = ? WHERE id = ?" % campo,
                                  (valor, id_registro))
    if ok and n == 0:
        return False, "Nenhum registro com id %s." % id_registro, 0
    return ok, msg, n


def excluir(id_registro):
    """DELETE por id."""
    ok, msg, n = executar_escrita("DELETE FROM registros WHERE id = ?", (id_registro,))
    if ok and n == 0:
        return False, "Nenhum registro com id %s." % id_registro, 0
    return ok, msg, n


# ---------------------------------------------------------------------------
# Entrada de dados pelo terminal (com tratamento de erros)
# ---------------------------------------------------------------------------
def ler_numero(pergunta, tipo=float):
    """Repete a pergunta até o usuário digitar um número válido."""
    while True:
        try:
            return tipo(input(pergunta).replace(",", "."))
        except ValueError:
            print("  Valor inválido: digite um número.")


def converter_campo(campo, texto):
    """Converte o texto digitado para o tipo certo do campo. Levanta ValueError se não der."""
    texto = texto.strip().replace(",", ".") if campo not in CAMPOS_TEXTO else texto.strip()
    if campo in CAMPOS_INTEIROS:
        return int(texto)
    if campo in CAMPOS_DECIMAIS:
        return float(texto)
    if campo == "status":
        texto = texto.lower()
        if texto not in STATUS_VALIDOS:
            raise ValueError("status deve ser: " + ", ".join(STATUS_VALIDOS))
    if not texto and campo != "mensagem":
        raise ValueError("campo obrigatório")
    return texto


def mostrar(linhas):
    """Imprime uma tabela simples."""
    if not linhas:
        print("  (nenhum registro)")
        return
    print("  %-4s %-11s %-5s %-8s %-8s %-8s %-11s %s" % (
        "ID", "Módulo", "Ciclo", "Consumo", "Bateria", "Temp", "Status", "Mensagem"))
    for r in linhas:
        print("  %-4d %-11s %-5d %-8.1f %-8.1f %-8.1f %-11s %s" % (
            r["id"], r["codigo_modulo"], r["ciclo"], r["consumo_kwh"], r["bateria_pct"],
            r["temperatura_c"], r["status"], r["mensagem"] or ""))


def menu_crud():
    while True:
        print("\n--- CRUD de registros ---")
        print(" 1. Cadastrar   2. Listar   3. Alterar   4. Excluir   0. Voltar")
        op = input("Opção: ").strip()
        if op == "0":
            return
        elif op == "1":
            registro = {}
            for campo in COLUNAS:
                while True:
                    try:
                        registro[campo] = converter_campo(campo, input("  %s: " % campo))
                        break
                    except ValueError as erro:
                        print("  Valor inválido (%s)." % erro)
            ok, msg, _ = cadastrar(registro)
            print(" ", msg)
            if ok:
                ao_registrar("Cadastrou %s ciclo %s" % (registro["codigo_modulo"], registro["ciclo"]))
        elif op == "2":
            print(" Filtrar por: 1) todos  2) módulo  3) status  4) ciclo")
            f = input(" Escolha: ").strip()
            if f == "2":
                mostrar(consultar("WHERE codigo_modulo = ?", (input(" Código (ex.: MOD-EN-001): ").strip().upper(),)))
            elif f == "3":
                mostrar(consultar("WHERE status = ?", (input(" Status: ").strip().lower(),)))
            elif f == "4":
                mostrar(consultar("WHERE ciclo = ?", (ler_numero(" Ciclo: ", int),)))
            else:
                mostrar(consultar())
        elif op == "3":
            id_reg = ler_numero(" ID do registro: ", int)
            campo = input(" Campo a alterar (%s): " % ", ".join(COLUNAS)).strip()
            try:
                valor = converter_campo(campo, input(" Novo valor: "))
            except ValueError as erro:
                print("  Valor inválido (%s)." % erro)
                continue
            ok, msg, _ = alterar(id_reg, campo, valor)
            print(" ", msg)
            if ok:
                ao_registrar("Alterou %s do id %d para %s" % (campo, id_reg, valor))
        elif op == "4":
            id_reg = ler_numero(" ID do registro: ", int)
            if input(" Confirma excluir o id %d? (s/n): " % id_reg).strip().lower() == "s":
                ok, msg, _ = excluir(id_reg)
                print(" ", msg)
                if ok:
                    ao_registrar("Excluiu o id %d" % id_reg)
            else:
                print("  Cancelado.")
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    preparar()
    print("Total no banco:", len(consultar()))
    for r in consultar("WHERE status = ?", ("alerta",)):
        print(" ", r["codigo_modulo"], "ciclo", r["ciclo"], "-", r["mensagem"])
