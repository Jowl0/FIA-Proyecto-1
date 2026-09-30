# Backend (FastAPI) que carga la red entrenada y clasifica autos en tiempo real.
#
# El modelo lo genera codigo/proyecto_1.py en app/backend/modelo/modelo.keras.
#
# Uso local (desde app/backend):
#   uvicorn main:app --reload
# Documentación interactiva: http://localhost:8000/docs
#
# El navegador no llama a esta API directamente: el frontend (Next.js) reenvía
# /api/* hacia aquí, por eso no hace falta CORS. En Docker solo es accesible
# desde la red interna.

from pathlib import Path
from typing import Literal

import numpy as np
import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel

RUTA_MODELO = Path(__file__).resolve().parent / "modelo" / "modelo.keras"

# Mismo encoding que en el entrenamiento (OrdinalEncoder con orden explícito):
# el índice de cada valor en la lista es el número que recibe la red
ORDEN_ATRIBUTOS = {
    "buying": ["low", "med", "high", "vhigh"],
    "maint": ["low", "med", "high", "vhigh"],
    "doors": ["2", "3", "4", "5more"],
    "persons": ["2", "4", "more"],
    "lug_boot": ["small", "med", "big"],
    "safety": ["low", "med", "high"],
}

# Salida de la red: LabelEncoder ordena alfabéticamente, la neurona i es CLASES[i]
CLASES = ["acc", "good", "unacc", "vgood"]

modelo = tf.keras.models.load_model(RUTA_MODELO)

app = FastAPI(title="Car Evaluation · Red neuronal")


class Auto(BaseModel):
    buying: Literal["low", "med", "high", "vhigh"]
    maint: Literal["low", "med", "high", "vhigh"]
    doors: Literal["2", "3", "4", "5more"]
    persons: Literal["2", "4", "more"]
    lug_boot: Literal["small", "med", "big"]
    safety: Literal["low", "med", "high"]


class Prediccion(BaseModel):
    clase: str
    probabilidades: dict[str, float]
    entrada: list[int]  # vector codificado que recibió la red


@app.get("/api/opciones")
def opciones() -> dict[str, list[str]]:
    """Valores válidos de cada atributo, en su orden natural."""
    return ORDEN_ATRIBUTOS


@app.post("/api/predecir")
def predecir(auto: Auto) -> Prediccion:
    """Codifica el auto, lo pasa por la red y devuelve la clase más probable."""
    entrada = [
        ORDEN_ATRIBUTOS[atributo].index(getattr(auto, atributo))
        for atributo in ORDEN_ATRIBUTOS
    ]
    salida = modelo(np.array([entrada], dtype="float32"), training=False).numpy()[0]
    return Prediccion(
        clase=CLASES[int(np.argmax(salida))],
        probabilidades={c: round(float(p), 4) for c, p in zip(CLASES, salida)},
        entrada=entrada,
    )
