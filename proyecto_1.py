# Equipo: Joel Reyes Garcia y Rodrigo Sosa Mendoza
# Materia: Fundamentos de inteligencia artificial

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Semilla fija para que los resultados sean reproducibles
tf.keras.utils.set_random_seed(42)

# Configurar estilo visual e-ink: papel crema, tinta negra, sin degradados
PAPEL = "#F2F2E9"
TINTA = "#121212"
GRIS = "#999999"

# JetBrains Mono si está instalada; si no (p. ej. en Colab), la monoespaciada por defecto
fuentes = {f.name for f in font_manager.fontManager.ttflist}
FUENTE = next(
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
        "font.monospace": [FUENTE, "DejaVu Sans Mono"],
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
    }
)
# Mapa de color de un solo tono: papel -> tinta
CMAP_EINK = LinearSegmentedColormap.from_list("eink", [PAPEL, TINTA])

# Las figuras se guardan junto a la presentación si existe; si no, en ./figuras
DIR_FIGURAS = "presentacion/figuras" if os.path.isdir("presentacion") else "figuras"
os.makedirs(DIR_FIGURAS, exist_ok=True)

pd.set_option("display.precision", 3)

# 1. Carga de datos del repositorio UCI (Car Evaluation, ID: 19)
print("Cargando el dataset...")
car_evaluation = fetch_ucirepo(id=19)
X = car_evaluation.data.features
y = car_evaluation.data.targets

# Unir X y y en un solo DataFrame
df = pd.concat([X, y], axis=1)

# Gráfico de la distribución de clases (de aceptable a muy bueno)
orden_clases = ["unacc", "acc", "good", "vgood"]
conteo = df["class"].value_counts().reindex(orden_clases)
porcentaje = conteo / conteo.sum() * 100

print("\nDistribución de clases:")
print(pd.DataFrame({"instancias": conteo, "porcentaje": porcentaje}))

fig, ax = plt.subplots(figsize=(8, 5))
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
    "Distribución de clases en Car Evaluation", fontsize=14, pad=15, fontweight="bold"
)
ax.set_ylim(0, conteo.max() * 1.18)  # Espacio para las etiquetas
sns.despine()

plt.tight_layout()
plt.savefig(os.path.join(DIR_FIGURAS, "distribucion_clases.png"), dpi=200)
plt.show()

# 2. Preprocesamiento de las características (X) con Ordinal Encoding
orden_buying = ["low", "med", "high", "vhigh"]
orden_maint = ["low", "med", "high", "vhigh"]
orden_doors = ["2", "3", "4", "5more"]
orden_persons = ["2", "4", "more"]
orden_lug_boot = ["small", "med", "big"]
orden_safety = ["low", "med", "high"]

ordinal_encoder = OrdinalEncoder(
    categories=[
        orden_buying,
        orden_maint,
        orden_doors,
        orden_persons,
        orden_lug_boot,
        orden_safety,
    ]
)

columnas_features = ["buying", "maint", "doors", "persons", "lug_boot", "safety"]
df_original = df.copy()  # Copia con los valores en texto, para comparar
df[columnas_features] = ordinal_encoder.fit_transform(df[columnas_features])

# Tabla de codificación: cada categoría se convierte en su posición (0, 1, 2, ...)
print("\n--- Codificación ordinal de los atributos ---")
for columna, categorias in zip(columnas_features, ordinal_encoder.categories_):
    mapeo = ", ".join(f"{c}->{i}" for i, c in enumerate(categorias))
    print(f"{columna:>9}: {mapeo}")

# 3. Preprocesamiento de la etiqueta objetivo (y)
label_encoder = LabelEncoder()
df["class_encoded"] = label_encoder.fit_transform(df["class"].values.ravel())

print("\n--- Codificación de la clase (LabelEncoder, orden alfabético) ---")
for i, clase in enumerate(label_encoder.classes_):
    print(f"{clase:>6} -> {i}")

# Preparemos los arreglos para la red neuronal
X_encoded = df[columnas_features].values
y_encoded = df["class_encoded"].values

# Ejemplo: lo que ve la red para los primeros autos (texto -> números)
print("\n--- Antes y después del encoding (primeras 5 filas) ---")
comparacion = pd.concat(
    [
        df_original[columnas_features + ["class"]].head(),
        df[columnas_features + ["class_encoded"]]
        .head()
        .astype(int)
        .rename(columns={"class_encoded": "class"})
        .add_suffix("_cod"),
    ],
    axis=1,
)
print(comparacion.to_string())

# La salida de la red es un vector de 4 probabilidades; la etiqueta k equivale
# al vector one-hot con un 1 en la posición k. 'sparse_categorical_crossentropy'
# hace esta conversión internamente, por eso no necesitamos one-hot explícito.
print("\n--- Etiqueta entera vs. vector one-hot equivalente ---")
for i, clase in enumerate(label_encoder.classes_):
    print(f"{clase:>6} = {i} -> {np.eye(4, dtype=int)[i]}")

# 4. División del dataset (80% entrenamiento, 20% prueba)
# (también se dividen los índices para poder recuperar la fila original)
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X_encoded, y_encoded, np.arange(len(df)), test_size=0.2, random_state=42
)

# 5. Construcción de la Red Neuronal (Perceptrón Multicapa - MLP)
modelo = Sequential(
    [
        Dense(32, activation="relu", input_shape=(X_train.shape[1],)),
        Dense(16, activation="relu"),
        Dense(4, activation="softmax"),
    ]
)

modelo.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

# 6. Entrenamiento imprimiendo cada época en consola
print("\nIniciando el entrenamiento de la red neuronal...\n")
historial = modelo.fit(
    X_train,
    y_train,
    epochs=60,
    batch_size=16,
    validation_split=0.2,
    verbose=1,  # Imprime cada época/generación en la terminal
)

# 7. Evaluación final con el conjunto de prueba
perdida, precision = modelo.evaluate(X_test, y_test, verbose=0)
print(f"\n--- Resultados Finales en Test ---")
print(f"Precisión del modelo: {precision * 100:.2f}%\n")

# 8. Predicciones y Gráfico Real vs Predicción (Matriz de Confusión)
print("Generando predicciones para graficar...\n")
predicciones_prob = modelo.predict(X_test)
predicciones_clases = np.argmax(predicciones_prob, axis=1)

# Recorrido completo de un auto del conjunto de prueba a través de la red:
# texto -> números -> red -> probabilidades (softmax) -> argmax -> texto
# (tomamos el primer auto "good" de prueba: su salida es más interesante que un "unacc")
i = int(np.flatnonzero(y_test == label_encoder.transform(["good"])[0])[0])
fila = df_original.iloc[idx_test[i]]
print("--- Ejemplo: un auto a través de la red ---")
print("Auto original:  ", dict(fila[columnas_features]))
print("Entrada a la red:", X_test[i].astype(int))
print("Salida softmax:  ", {c: f"{p:.3f}" for c, p in zip(label_encoder.classes_, predicciones_prob[i])})
print("argmax:          ", predicciones_clases[i])
print("Predicción:      ", label_encoder.inverse_transform([predicciones_clases[i]])[0])
print("Clase real:      ", fila["class"], "\n")

# Matriz en el orden natural de las clases (peor -> mejor) para que las
# clases vecinas queden juntas y se vea entre cuáles se equivoca la red
orden_matriz = label_encoder.transform(orden_clases)
cm = confusion_matrix(y_test, predicciones_clases, labels=orden_matriz)

# Métricas por clase: precisión (de lo que predijo como X, cuánto era X)
# y recall (de los X reales, cuántos encontró)
print(
    classification_report(
        y_test, predicciones_clases, labels=orden_matriz, target_names=orden_clases
    )
)

plt.figure(figsize=(8, 6))

# Matriz de confusión con mejor estilo visual
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
    xticklabels=orden_clases,
    yticklabels=orden_clases,
)

# Estilización de las etiquetas y título
plt.xlabel("Predicción del Modelo", fontsize=12, fontweight="bold")
plt.ylabel("Valor Real", fontsize=12, fontweight="bold")
plt.title(
    "Matriz de Confusión: Real vs Predicción", fontsize=14, pad=15, fontweight="bold"
)

# Ajuste de las rotaciones de los nombres para que se lean mejor
plt.xticks(rotation=45, ha="right", fontsize=11)
plt.yticks(rotation=0, fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(DIR_FIGURAS, "matriz_confusion.png"), dpi=200)
plt.show()
