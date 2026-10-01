# Proyecto 1 — Clasificación de *Car Evaluation* con redes neuronales

**Equipo:** Joel Reyes García y Rodrigo Sosa Mendoza
**Materia:** Fundamentos de Inteligencia Artificial

Clasificación de la aceptabilidad de automóviles (`unacc`, `acc`, `good`, `vgood`)
del conjunto [Car Evaluation](https://archive.ics.uci.edu/dataset/19/car+evaluation)
(UCI) con un perceptrón multicapa en TensorFlow/Keras.

**Demo en vivo:** <https://fia.jowlab.com>

## Resultados

| | |
|---|---|
| Arquitectura | MLP 6 → 32 → 16 → 4 (ReLU, ReLU, softmax) · 820 parámetros |
| Entrenamiento | Adam · 250 épocas · lotes de 16 · 20 % de validación |
| Exactitud en prueba | **95.66 %** (331 de 346) |

La mayoría de los errores ocurren entre clases vecinas (`unacc`↔`acc`, `good`↔`vgood`).

## Estructura

```
.
├── codigo/
│   ├── proyecto_1.py        # carga, encoding, entrenamiento, evaluación y guardado del modelo
│   └── graficas.py          # gráficas con estilo e-ink (distribución y matriz de confusión)
├── presentacion/
│   ├── main.tex             # diapositivas (Beamer)
│   ├── beamerthemeeink.sty  # tema e-ink
│   ├── referencias.bib
│   └── figuras/             # gráficas generadas por el script
└── app/
    ├── compose.yaml         # backend + frontend + túnel de Cloudflare
    ├── backend/             # FastAPI: carga modelo/modelo.keras y predice
    │   └── modelo/          # red entrenada (no se versiona; la genera el script)
    └── frontend/            # Next.js: formulario y predicción en tiempo real
```

## Entrenar la red

```bash
python codigo/proyecto_1.py
```

Genera las figuras en `presentacion/figuras/` y guarda la red entrenada en
`app/backend/modelo/modelo.keras`. El modelo no está en el repositorio: hay que
entrenar al menos una vez después de clonar, antes de levantar la app. La
semilla es fija, así que los resultados se repiten en cada ejecución.

Dependencias: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`,
`tensorflow`, `ucimlrepo`.

> En Colab hay que subir también `graficas.py`; las figuras y el modelo se
> guardan en `./figuras` y `./modelo`.

## Presentación

```bash
cd presentacion
latexmk main.tex   # LuaLaTeX; PDF en presentacion/build/main.pdf
```

## App web

Un formulario donde se eligen las características de un auto y la red lo
clasifica en tiempo real.

```
navegador ─► frontend (Next.js :3000) ──red interna──► backend (FastAPI :8000)
```

Solo el frontend se expone; el backend vive en una red interna de Docker sin
salida a internet. El frontend reenvía `/api/opciones` y `/api/predecir` al
backend.

### Con Docker

Requiere haber entrenado la red (ver arriba).

```bash
cp .env.example .env   # poner TUNNEL_TOKEN del túnel de Cloudflare
cd app
docker compose up -d --build   # http://localhost:3000
```

El túnel de Cloudflare debe apuntar a `http://frontend:3000`. Si el puerto
3000 está ocupado: `FRONT_PORT=3200 docker compose up -d --build`.

Después de reentrenar la red, reconstruir el backend para que use el modelo
nuevo: `docker compose up -d --build backend`.

### Sin Docker (desarrollo)

```bash
cd app/backend && uvicorn main:app --reload   # http://localhost:8000/docs
cd app/frontend && pnpm install && pnpm dev    # http://localhost:3000
```
