import random

modulos    = []   # lista geral de todos os modulos cadastrados
fila_pouso = []   # fila de pouso FIFO (ordem de chegada a órbita)
pilha_emer = []   # pilha de emergência LIFO (modulos criticos primeiro)

# Listas auxiliares de status pos autorizacao
pousados  = []
em_espera = []
em_alerta = []

# Cadastro dos modulos
def cadastrar(nome, tipo, prioridade, combustivel, massa_ton, criticidade, horario_orbita, sensores_ok=True, atmosfera_ok=True):
    """Cadastra um modulo da espaçonave e insere na lista e na fila

        Atributos:
        nome (str): Identificador do modulo
        tipo (str): Habitacao, Energia, Laboratorios, Logistica, Medico
        prioridade (int): 1= alta, 2= media, 3= baixa
        combustivel (int): percentual restante de combustivel (0-10%)
        massa_ton (float): massa do modulo em toneladas(ton)
        criticidade (str): "alta", "media" ou "baixa"
        horario_orbita (str): horario estimado de chegada a orbita (ex: 8:30)
        sensores_ok (bool): integridade dos sensores de navegacao
        atmosfera_ok (bool): condicao atmosferica simula favoravel ao pouso

    """

    mod = {
        "nome":   nome,
        "tipo":   tipo,
        "prior":  prioridade,
        "comb":   combustivel,
        "massa":  massa_ton,
        "critic": criticidade,
        "orbita": horario_orbita,
        "sensores": sensores_ok, # True = sensores integros 
        "atmosfera": atmosfera_ok, # True = condicoes atmosfericas favoraveis
        "ok":     False  # Sera definido pela logica de autorizacao

   }
    modulos.append(mod)
    fila_pouso.append(mod)
    print(f"[+] {nome} ({tipo}) - chegada a orbita: {horario_orbita}")



# Portas Logicas e Funcoes que simulam AND, OR e NOT 
AND = lambda a, b: a and b
OR = lambda a, b: a or b
NOT = lambda a: not a


# Autorizacao De pouso usando if, elif, else
def autorizar(mod, pista_livre):
    """Decide a autorizacao de pouso usando funcoes booleanas"""
    comb_critico = mod["comb"] <= 15 # combustivel critico?
    eh_medica  = mod["tipo"] == "medica" # carga medica?
    prior_alta  = mod["prior"] == 1 # prioridade max?
    critic_alta = mod["critic"] == "alta" # carga de alta criticidade
    sensor_falha = NOT(mod["sensores"]) # NOT - sensor com problema
    atm_ruim     = NOT(mod["atmosfera"]) # NOT - atmosfera desfavoravel 

    if OR(sensor_falha, atm_ruim): # bloqueio imediato
        return False, "Bloqueado: falha de sensor ou atmosfera desfavoravel"
    
    elif AND(comb_critico, pista_livre):
        return True, "Emergencia: combustivel critico"
    
    elif AND(prior_alta, pista_livre):
        return True, "Prioridade maxima! pouso autorizado"
    
    elif NOT(pista_livre):
        return False, "ditch indisponivel, aguardar orbita."
    
    elif mod["comb"] > 30 and mod["prior"] > 2:
        return False, "Combustivel estavel! aguardar na fila"
    
    else:
        return True, "Condicoes normais, pouso liberado"
    

# Busca Linear
def buscar_tipo(tipo):
    """Retorna todas as espaconaves de um determinado tipo de carga"""
    return [m for m in modulos if m["tipo"] == tipo]

def menor_combustivel():
    """Retorna o modulo com menos combustivel (mais critica)"""
    return min(modulos, key=lambda m: m["comb"])

def buscar_criticidade(nivel):
    """Busca modulos por nivel de criticidade da carga"""
    return [m for m in modulos if m["critic"] == nivel ]

# Funcao Matematica, Altura de Descida
# Modelo: funcao linear h(t) = h0 - v * t
# h0 = altura inicial (km), v = velocidade media de descida (km/s), t = tempo (s)
# usadaa para estimar o momento de acionar retrofoguetes (h <= 10km)
def altura_descida(h0, v, t):
    """Retorna a altura do modelo em km no instante t (segundos)"""
    return h0 - v * t

def simular_descida(nome, h0=120, v=0.5):
    """Simula a descida e indica quando acionar os retrofoguetes (h <= 10km)
       h(t) = h0 - v * t > funcao linear decrescente
    """
    print(f"\n Simulacao de descida: {nome}")
    print(f" h(t) = {h0} - {v} * t (km)")
    for t in range(0, 300, 40):
        h = altura_descida(h0, v, t)
        alerta = "ACIONAR RETROFOGUETES" if h <= 10 else""
        print(f" t={t:3}s > h={h:6.1f} km{alerta}")
        if h <= 0:
            break

# Ordena por combustível crescente
def bubble_sort(lista):
    """Modulos com menos combustivel sobem para o inicio da fila"""
    lst = lista[:]
    for i in range(len(lst) - 1):
        for j in range(len(lst) - 1 - i):
            if lst[j]["comb"] > lst[j+1]["comb"]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst

# Ordena por prioridade crescente
def selection_sort(lista):
        """Modulos com prioridade 1 (mais urgente) ficam no topo da fila"""
        lst = lista[:]
        for i in range(len(lst)):
            idx = min(range(i, len(lst)), key=lambda j: lst[j]["prior"])
            lst[i], lst[idx] = lst[idx], lst[i]
            return lst

# Pilha de emergencia
def push_emergencia(mod):
        """Empilha modulo em emergencia (Push)"""
        pilha_emer.append(mod)
        print(f" [!] EMERGENCIA: {mod['nome']} empilhado para pouso imediato")

def pop():
        """Desempilha o modulo mais urgente (pop)"""
        return pilha_emer.pop() if pilha_emer else None

# Log de autorizacao
def log_status(mod, ok, msg):
        """Exibe o resultado da autorizacao de forma legivel"""
        status = "Ok" if ok else "Erro"
        print(f" [{mod['nome']}] {status} - {msg}")

# Exibicao
def exibir(lista, titulo):
    print(f"\n{'─'*62}\n  {titulo}\n{'─'*62}")
    for m in lista:
        s = "Correto" if m["ok"] else "Esperando"  # ← 8 espaços
        print(f"  {s} {m['nome']:14} | {m['tipo']:12} | comb:{m['comb']:3}% "
              f"| prior:{m['prior']} | {m['massa']:5.1f}t | critic:{m['critic']:5} | {m['orbita']}")
        
# Relatorio ESG
def relatorio_esg():
    """E = ambiental, S = social, G = governanca"""
    massa_total = sum(m["massa"] for m in modulos)
    medicas = sum(1 for m in modulos if m["tipo"] == "medicas")
    aprov = sum(1 for m in modulos if m["ok"])
    print(f"\n{'=' * 62}")
    print(" Relatorio ESG - Missao Aurora Siger > Terra")
    print(f" [E] Massa total pousada: {massa_total:.1f} t")
    print(f" [S] Modulos medicos priorizados: {medicas}")
    print(f" [G] Autorizados: {aprov}/{len(modulos)}")
    f"({aprov}/{len(modulos)})"
    print(f"{'=' * 62}")

# Programa principal
if __name__ == "__main__":

    print("=" * 62)
    print("MGPEB - Missao Espacial Aurora Siger")
    print("Sistema de Gerenciamento de Pouso")
    print("=" * 62)

    # atributos: nome, tipo, prior, comb(%), massa(t), critic, orbita, sensores, atmosf
    print("\n[1] CADASTRO DOS MODULOS")
    cadastrar("MOD-HAB-01", "habitacao", 2, 65, 18.5, "media", "07:00")
    cadastrar("MOD-ENE-01", "energia",  1, 40, 12.0, "alta", "07:30")
    cadastrar("MOD-LAB-01", "laboratorio",  2, 55, 9.8, "media", "08:00")
    cadastrar("MOD-LAB-01", "logistica",  3, 80, 22.0, "baixa", "08:45")
    cadastrar("MOD-MED-01", "medica", 1, 60, 7.5, "alta", "07:15")
    cadastrar("MOD-ENE-02", "energia", 2, 10, 11.0, "alta", "06:50")
    cadastrar("MOD-HAB-02", "habitacao",   3, 90, 19.0, "baixa", "09:00",
              sensores_ok=False)
    cadastrar("MOD-LAB-02", "laboratorio", 2, 50,  8.5, "media", "08:30",
              atmosfera_ok=False)
    
    exibir(fila_pouso, "FILA INICIAL! ordem de chegada a orbita")

    # Pilha de  emergencia
print("\n[2] PILHA DE EMERGENCIA (combustivel ≤ 15%)")
for m in modulos:
    if m["comb"] <= 15:
        push_emergencia(m)

# Busca
print("\n[3] BUSCA NAS ESTRUTURAS")
print("  Modulos medicos:", [m["nome"] for m in buscar_tipo("medico")])
print("  Criticidade alta:", [m["nome"] for m in buscar_criticidade("alta")])
crit = menor_combustivel()
print(f"  Menor combustível: {crit['nome']} ({crit['comb']}%)")

# Ordenacao
print("\n[4] ORDENAÇAO DA FILA")
exibir(bubble_sort(fila_pouso),    "Bubble Sort por combustivel (mais critico primeiro)")
exibir(selection_sort(fila_pouso), "Selection Sort por prioridade (mais urgente primeiro)")

# Autorizacao de pouso
print("\n[5] AUTORIZACAO DE POUSO")

# Emergencias primeiro, pilha LIFO
print(" Atendendo pilha de emergencia: ")
while pilha_emer:
    m = pop()
    ok, msg = autorizar(m, pista_livre=True)
    m["ok"] = ok
    pousados.append(m) if ok else em_alerta.append(m)
    log_status(m, ok, msg)

# Fila ordenada prioridadade
print("  >> Processando fila por prioridade:")
pista = True
for m in selection_sort(fila_pouso):
    ok, msg = autorizar(m, pista_livre=pista)
m["ok"] = ok
pista = not ok
if ok:
    pousados.append(m)
elif not m["sensores"] or not m["atmosfera"]:
    em_alerta.append(m)
else:
    em_espera.append(m)
log_status(m, ok, msg)
 
exibir(modulos,   "STATUS FINAL DOS MÓDULOS")
exibir(pousados,  "MODULOS POUSADOS COM SUCESSO")
exibir(em_espera, "MODULOS EM ESPERA (fila)")
exibir(em_alerta, "MODULOS EM ALERTA (bloqueados)")

# Relatorio ESG
print("\n[6] RELATORIO ESG")
relatorio_esg()
 
# FUNÇÃO MATEMATICA
# h(t) = h0 - v * t  | função linear decrescente
print("\n[7] MODELAGEM MATEMÁTICA ALTURA DE DESCIDA")
simular_descida("MOD-MED-01", h0=120, v=0.5)
 
print("\n  Missao Aurora Siger concluida. Bem vindos a Marte \n")
