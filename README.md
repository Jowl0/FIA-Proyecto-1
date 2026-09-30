# Proyecto 1 — Clasificación de *Car Evaluation* con redes neuronales

**Equipo:** Joel Reyes García y Rodrigo Sosa Mendoza
**Materia:** Fundamentos de Inteligencia Artificial

Clasificación de la aceptabilidad de automóviles (`unacc`, `acc`, `good`, `vgood`)
del conjunto [Car Evaluation](https://archive.ics.uci.edu/dataset/19/car+evaluation)
(UCI) con un perceptrón multicapa en TensorFlow/Keras.

## Estructura

```
.
├── codigo/
│   └── proyecto_1.py      # carga, encoding, entrenamiento de la red, métricas y gráficas
├── documentacion/
│   └── proyecto_1.md      # explicación del código paso a paso
└── presentacion/
    ├── main.tex           # diapositivas (Beamer)
    ├── beamerthemeeink.sty
    ├── referencias.bib
    └── figuras/           # gráficas generadas por el script
```

## Uso

Entrenar la red (genera las figuras en `presentacion/figuras/`):

```bash
python codigo/proyecto_1.py
```

Dependencias: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`,
`tensorflow`, `ucimlrepo`.

Compilar la presentación (LuaLaTeX):

```bash
cd presentacion && latexmk main.tex   # PDF en presentacion/build/main.pdf
```
