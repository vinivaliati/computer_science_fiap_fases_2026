# arquivo temporario para gerar os graficos do projeto
# pode ser apagado apos uso

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.gerar    import gerar_dados
from src.energia  import analisar_balanco
from src.decisao  import decidir, classificar_status
from src.previsao import calcular_regressao, prever


CORES_BALANCO = {
    'DEFICIT':     '#e05c5c',
    'EQUILIBRADO': '#5b9bd5',
    'EXCEDENTE':   '#5cb85c',
}
CORES_STATUS = {
    'EMERGENCIA': '#8b0000',
    'ALERTA':     '#e07b00',
    'AVISO':      '#c8a800',
    'NORMAL':     '#d4d4d4',
}


def gerar_graficos():
    registros   = gerar_dados()
    processados = [
        {'registro': r, 'balanco': analisar_balanco(r), 'acoes': decidir(r)}
        for r in registros
    ]
    a, b = calcular_regressao(registros)
    ordenados = sorted(processados, key=lambda p: p['registro']['dia'])

    fig = plt.figure(figsize=(13, 10))
    fig.suptitle('Colônia Espacial Marte-I — Análise Anual', fontsize=14, fontweight='bold', y=0.98)

    # layout: grafico 1 ocupa metade, grafico 2 ocupa 40%, faixa de status 10%
    gs = fig.add_gridspec(3, 1, height_ratios=[5, 4, 1], hspace=0.45)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2], sharex=ax2)

    # --- grafico 1: regressao linear ---
    x_vals  = [r['irradiancia_solar'] for r in registros]
    y_vals  = [r['energia_gerada']    for r in registros]
    x_reta  = [min(x_vals), max(x_vals)]
    y_reta  = [prever(x, a, b) for x in x_reta]

    ax1.scatter(x_vals, y_vals, color='#5b9bd5', alpha=0.35, s=18, label='Dados reais')
    ax1.plot(x_reta, y_reta, color='#e05c5c', linewidth=2,
             label=f'Regressão: energia = {a} × irradiância + {b}')
    ax1.set_title('Regressão Linear — Irradiância Solar × Energia Gerada', fontsize=11)
    ax1.set_xlabel('Irradiância Solar (W/m²)')
    ax1.set_ylabel('Energia Gerada (kWh)')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.25)

    # --- grafico 2: balanco diario ---
    dias    = [p['registro']['dia'] for p in ordenados]
    balanco = [p['balanco']['balanco'] for p in ordenados]
    cores_b = [CORES_BALANCO[p['balanco']['status']] for p in ordenados]

    ax2.bar(dias, balanco, color=cores_b, width=1.0, alpha=0.9, zorder=2)
    ax2.axhline(0, color='#333333', linewidth=0.9, linestyle='--', zorder=3)
    ax2.set_title('Balanço Energético Diário (kWh)', fontsize=11)
    ax2.set_ylabel('Balanço (kWh)')
    ax2.grid(True, alpha=0.2, axis='y', zorder=1)

    legendas = [mpatches.Patch(color=c, label=s) for s, c in CORES_BALANCO.items()]
    ax2.legend(handles=legendas, fontsize=8, loc='lower right', ncol=3)
    plt.setp(ax2.get_xticklabels(), visible=False)

    # --- grafico 3: faixa de status de decisao ---
    for i, p in enumerate(ordenados):
        status = classificar_status(p['acoes'])
        ax3.bar(dias[i], 1, color=CORES_STATUS[status], width=1.0, alpha=0.95)

    ax3.set_yticks([])
    ax3.set_xlabel('Dia do Ano')
    ax3.set_title('Status das Decisões', fontsize=9, pad=3)

    legendas_s = [mpatches.Patch(color=c, label=s) for s, c in CORES_STATUS.items()]
    ax3.legend(handles=legendas_s, fontsize=7, loc='lower right', ncol=4,
               bbox_to_anchor=(1, 1.05))

    plt.savefig('graficos_colonia.png', dpi=150, bbox_inches='tight')
    print("Grafico salvo em: graficos_colonia.png")
    plt.show()


if __name__ == '__main__':
    gerar_graficos()