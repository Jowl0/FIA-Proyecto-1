# Equipo: Joel Reyes Garcia y Rodrigo Sosa Mendoza
# Materia: Fundamentos de inteligencia artificial
#
# Gráficas del proyecto 1 con estilo e-ink (papel crema, tinta negra, sin
# degradados). Las usa proyecto_1.py:
#
#   from graficas import aplicar_estilo_eink, grafica_distribucion, grafica_matriz_confusion

import os

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

PAPEL = "#F2F2E9"
TINTA = "#121212"
GRIS = "#999999"

# Mapa de color de un solo tono: papel -> tinta
CMAP_EINK = LinearSegmentedColormap.from_list("eink", [PAPEL, TINTA])

# Las figuras se guardan junto a la presentación si existe (ejecutando desde la
# raíz del repo o desde codigo/); si no (p. ej. en Colab), en ./figuras
DIR_FIGURAS = next(
    (
        d
        for d in ["presentacion/figuras", "../presentacion/figuras"]
        if os.path.isdir(d)
    ),
    "figuras",
)


def aplicar_estilo_eink():
    """Configura matplotlib/seaborn con el estilo e-ink para todas las gráficas."""
    # JetBrains Mono si está instalada; si no (p. ej. en Colab), la monoespaciada por defecto
    fuentes = {f.name for f in font_manager.fontManager.ttflist}
    fuente = next(
        (f for f in ["JetBrainsMono NFM", "JetBrains Mono"] if f in fuentes),
        "DejaVu Sans Mono",
    )

    sns.set_theme(style="ticks")
    plt.rcParams.update(
        {
            "figure.facecolor": PAPEL,
            "axes.facecolor": PAPEL,
            "savefig.facecolor": PAPEL,
            "axes.edgecolor": TINTA,
            "axes.labelcolor": TINTA,
            "axes.linewidth": 1.5,
            "axes.grid": False,
            "text.color": TINTA,
            "xtick.color": TINTA,
            "ytick.color": TINTA,
            "font.family": "monospace",
            "font.monospace": [fuente, "DejaVu Sans Mono"],
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",
        }
    )


def _guardar_y_mostrar(nombre):
    os.makedirs(DIR_FIGURAS, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, nombre), dpi=200)
    plt.show()


def grafica_distribucion(conteo):
    """Barras con el número de instancias por clase (conteo: Serie clase -> n)."""
    porcentaje = conteo / conteo.sum() * 100

    _, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(
        conteo.index,
        conteo.to_numpy(),
        color=TINTA,
        edgecolor=TINTA,
        width=0.6,
    )

    # Etiqueta encima de cada barra: número de instancias y porcentaje
    for barra, n, p in zip(barras, conteo.values, porcentaje.values):
        ax.annotate(
            f"{n}\n({p:.1f}%)",
            xy=(barra.get_x() + barra.get_width() / 2, barra.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_xlabel("Clase", fontsize=12, fontweight="bold")
    ax.set_ylabel("Número de instancias", fontsize=12, fontweight="bold")
    ax.set_title(
        "Distribución de clases en Car Evaluation",
        fontsize=14,
        pad=15,
        fontweight="bold",
    )
    ax.set_ylim(0, conteo.max() * 1.18)  # Espacio para las etiquetas
    sns.despine()

    _guardar_y_mostrar("distribucion_clases.png")


def grafica_matriz_confusion(cm, etiquetas):
    """Matriz de confusión (filas: valor real, columnas: predicción)."""
    plt.figure(figsize=(8, 6))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap=CMAP_EINK,  # Un solo tono: papel (0) -> tinta (máximo)
        cbar=True,  # Agrega la barra lateral de escala de colores
        linewidths=2,  # Agrega líneas de separación entre las celdas
        linecolor=TINTA,  # Bordes de tinta, como las ventanas de Hyprland
        square=True,  # Fuerza a que las celdas sean cuadradas perfectas
        annot_kws={
            "size": 14,
            "weight": "bold",
        },  # Hace los números interiores más legibles
        xticklabels=etiquetas,
        yticklabels=etiquetas,
    )

    # Estilización de las etiquetas y título
    plt.xlabel("Predicción del Modelo", fontsize=12, fontweight="bold")
    plt.ylabel("Valor Real", fontsize=12, fontweight="bold")
    plt.title(
        "Matriz de Confusión: Real vs Predicción",
        fontsize=14,
        pad=15,
        fontweight="bold",
    )

    # Ajuste de las rotaciones de los nombres para que se lean mejor
    plt.xticks(rotation=45, ha="right", fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    _guardar_y_mostrar("matriz_confusion.png")
