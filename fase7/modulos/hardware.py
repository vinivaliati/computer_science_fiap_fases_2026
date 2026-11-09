"""
hardware.py - circuito lógico, Arduino e Tinkercad (etapa 6).

O circuito do Tinkercad usa as MESMAS 4 variáveis e expressões de regras.py:
    RISCO  = (B AND E) OR (C AND T)   -> LED vermelho + buzzer
    ALERTA = B OR C OR T              -> LED amarelo
    NORMAL = NOT ALERTA               -> LED verde

Montagem (Arduino Uno):
  Entradas                              Pino    Variável
  Potenciômetro 1 (nível da bateria)    A0      B = bateria < 25 %
  Sensor de temperatura TMP36           A1      T = temperatura > 26 °C
  Potenciômetro 2 (consumo / média)     A2      C = consumo > 120 % da média
  Chave deslizante (módulo essencial)   D2      E
  Saídas
  LED vermelho + resistor 220 ohms      D8      RISCO
  LED amarelo  + resistor 220 ohms      D9      ALERTA
  LED verde    + resistor 220 ohms      D10     NORMAL
  Buzzer piezo                          D11     RISCO
"""
import regras


def ler_sensores_simulados(bateria_pct, temperatura_c, consumo_pct_media, essencial):
    """Converte os valores 'físicos' nas 4 variáveis booleanas, como o Arduino faz."""
    return (bateria_pct < regras.LIMITE_BATERIA,
            bool(essencial),
            consumo_pct_media > regras.FATOR_CONSUMO * 100,
            temperatura_c > regras.LIMITE_TEMPERATURA)


def simular_circuito(bateria_pct, temperatura_c, consumo_pct_media, essencial):
    b, e, c, t = ler_sensores_simulados(bateria_pct, temperatura_c, consumo_pct_media, essencial)
    risco, alerta = regras.avaliar(b, e, c, t)
    return {"B": b, "E": e, "C": c, "T": t,
            "led_vermelho": risco, "buzzer": risco,
            "led_amarelo": alerta, "led_verde": not alerta}


def menu_hardware():
    print(__doc__)
    cenarios = [
        ("Operação normal",                70, 22, 100, False),
        ("Temperatura alta isolada",       70, 28, 100, False),
        ("Bateria baixa, módulo comum",    20, 22, 100, False),
        ("Bateria baixa, módulo essencial", 20, 22, 100, True),
        ("Consumo alto + temperatura alta", 70, 29, 140, False),
    ]
    print("  Cenários simulados (mesma lógica do circuito no Tinkercad):")
    print("  %-34s B E C T  Verde Amarelo Vermelho Buzzer" % "")
    for nome, bat, temp, cons, ess in cenarios:
        r = simular_circuito(bat, temp, cons, ess)
        print("  %-34s %d %d %d %d    %d      %d       %d       %d" % (
            nome, r["B"], r["E"], r["C"], r["T"], r["led_verde"], r["led_amarelo"],
            r["led_vermelho"], r["buzzer"]))
    print("\n  Diagrama das portas lógicas: circuito_logico.png (na raiz do projeto)")
    print("  Circuito Arduino: veja link_tinkercad.txt")


if __name__ == "__main__":
    menu_hardware()
