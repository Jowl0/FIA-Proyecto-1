## Importamos el dataframe

``` python

import numpy as np
import pandas as pd
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# 1. Carga de datos
car_evaluation = fetch_ucirepo(id=19)
X = car_evaluation.data.features
y = car_evaluation.data.targets

```

``` python 

# 2. Preprocesamiento de las características (X) con Ordinal Encoding
orden_buying = ['low', 'med', 'high', 'vhigh']
orden_maint = ['low', 'med', 'high', 'vhigh']
orden_doors = ['2', '3', '4', '5more']
orden_persons = ['2', '4', 'more']
orden_lug_boot = ['small', 'med', 'big']
orden_safety = ['low', 'med', 'high']

ordinal_encoder = OrdinalEncoder(categories=[
    orden_buying, orden_maint, orden_doors, 
    orden_persons, orden_lug_boot, orden_safety
])

X_encoded = ordinal_encoder.fit_transform(X)

# 3. Preprocesamiento del objetivo (y)
# LabelEncoder convierte ['unacc', 'acc', 'good', 'vgood'] en [0, 1, 2, 3]
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y.values.ravel())

# 4. División del dataset (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, random_state=42
)

```


```python 

# 5. Construcción de la Red Neuronal
modelo = Sequential([
    # Capa de entrada (6 neuronas porque hay 6 características) y primera capa oculta
    Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    # Segunda capa oculta
    Dense(16, activation='relu'),
    # Capa de salida (4 neuronas porque hay 4 clases). Softmax da probabilidades que suman 1.
    Dense(4, activation='softmax')
])

# Compilación del modelo
# 'sparse_categorical_crossentropy' es la función de pérdida ideal cuando 
# las etiquetas son enteros (0, 1, 2, 3) en lugar de One-Hot Encoding.
modelo.compile(
    optimizer='adam', 
    loss='sparse_categorical_crossentropy', 
    metrics=['accuracy']
)

# 6. Entrenamiento
print("Iniciando el entrenamiento...")
historial = modelo.fit(
    X_train, y_train, 
    epochs=60, 
    batch_size=16, 
    validation_split=0.2, # Usa 20% del set de entrenamiento para validar en cada época
    verbose=1
)

# 7. Evaluación final con los datos de prueba que la red nunca ha visto
perdida, precision = modelo.evaluate(X_test, y_test, verbose=0)
print(f"\n--- Resultados Finales en Test ---")
print(f"Precisión del modelo: {precision * 100:.2f}%")

```

