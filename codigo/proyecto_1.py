# Equipo: Joel Reyes Garcia y Rodrigo Sosa Mendoza
# Materia: Fundamentos de inteligencia artificial

import os

import numpy as np
import tensorflow as tf
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.metrics import confusion_matrix
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from graficas import aplicar_estilo_eink, grafica_distribucion, grafica_matriz_confusion

# Reproducibilidad
tf.keras.utils.set_random_seed(42)
aplicar_estilo_eink()

# 1. Carga de datos
car_evaluation = fetch_ucirepo(id=19)
X = car_evaluation.data.features
y = car_evaluation.data.targets

# Distribución de clases (peor -> mejor)
orden_clases = ["unacc", "acc", "good", "vgood"]
grafica_distribucion(y["class"].value_counts().reindex(orden_clases))

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

X_encoded = ordinal_encoder.fit_transform(X)

# 3. Preprocesamiento del objetivo (y)
# LabelEncoder usa orden alfabético: acc=0, good=1, unacc=2, vgood=3
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y.values.ravel())

# 4. División del dataset (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, random_state=42
)

# 5. Construcción de la Red Neuronal
modelo = Sequential(
    [
        # Entrada (6 características) y primera capa oculta
        Dense(32, activation="relu", input_shape=(X_train.shape[1],)),
        # Segunda capa oculta
        Dense(16, activation="relu"),
        # Salida: 4 clases, softmax da probabilidades que suman 1
        Dense(4, activation="softmax"),
    ]
)

# Etiquetas enteras (no one-hot) -> sparse_categorical_crossentropy
modelo.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

# 6. Entrenamiento
print("Iniciando el entrenamiento...")
historial = modelo.fit(
    X_train,
    y_train,
    epochs=250,
    batch_size=16,
    validation_split=0.2,  # 20% del entrenamiento para validar en cada época
    verbose=1,
)

# 7. Evaluación final con los datos de prueba
perdida, precision = modelo.evaluate(X_test, y_test, verbose=0)
print(f"\n--- Resultados Finales en Test ---")
print(f"Precisión del modelo: {precision * 100:.2f}%")

# Guardar la red entrenada para el backend (en Colab: ./modelo)
dir_modelo = next(
    (d for d in ["app/backend", "../app/backend"] if os.path.isdir(d)), "."
)
ruta_modelo = os.path.join(dir_modelo, "modelo", "modelo.keras")
os.makedirs(os.path.dirname(ruta_modelo), exist_ok=True)
modelo.save(ruta_modelo)
print(f"Modelo guardado en {ruta_modelo}")

# 8. Matriz de confusión (clases en orden peor -> mejor)
predicciones = np.argmax(modelo.predict(X_test), axis=1)
cm = confusion_matrix(
    y_test, predicciones, labels=label_encoder.transform(orden_clases)
)
grafica_matriz_confusion(cm, orden_clases)
