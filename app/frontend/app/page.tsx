"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";
import BotonTema from "./BotonTema";

type Auto = Record<string, string>;
type Prediccion = {
  clase: string;
  probabilidades: Record<string, number>;
  entrada: number[];
};

// Nombre en español de cada atributo (las claves vienen del backend)
const ETIQUETAS: Record<string, string> = {
  buying: "Precio de compra",
  maint: "Mantenimiento",
  doors: "Puertas",
  persons: "Personas",
  lug_boot: "Cajuela",
  safety: "Seguridad",
};

// Clases en su orden natural (peor -> mejor) para mostrar las barras
const CLASES = [
  { id: "unacc", nombre: "inaceptable" },
  { id: "acc", nombre: "aceptable" },
  { id: "good", nombre: "bueno" },
  { id: "vgood", nombre: "muy bueno" },
];

// Auto inicial: el ejemplo de la presentación (la red duda entre good y acc)
const AUTO_INICIAL: Auto = {
  buying: "low",
  maint: "med",
  doors: "5more",
  persons: "more",
  lug_boot: "med",
  safety: "med",
};

export default function Home() {
  const [opciones, setOpciones] = useState<Record<string, string[]> | null>(null);
  const [auto, setAuto] = useState<Auto>(AUTO_INICIAL);
  const [prediccion, setPrediccion] = useState<Prediccion | null>(null);
  // Auto al que corresponde la predicción mostrada y cuánto tardó en llegar
  const [respondido, setRespondido] = useState({ auto: "", ms: 0 });
  const [error, setError] = useState<string | null>(null);

  // Valores válidos de cada atributo
  useEffect(() => {
    fetch("/api/opciones")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setOpciones)
      .catch(() => setError("No se pudo conectar con el backend"));
  }, []);

  // Predicción en tiempo real: cada cambio del auto se manda a la red
  useEffect(() => {
    const control = new AbortController();
    const inicio = performance.now();
    fetch("/api/predecir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(auto),
      signal: control.signal,
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((p: Prediccion) => {
        setPrediccion(p);
        setRespondido({ auto: JSON.stringify(auto), ms: performance.now() - inicio });
        setError(null);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(`Error al predecir: ${e.message}`);
      });
    return () => control.abort();
  }, [auto]);

  const claseActual = CLASES.find((c) => c.id === prediccion?.clase);
  // Hay una petición en camino si el auto cambió y aún no llega su respuesta
  const calculando = prediccion !== null && respondido.auto !== JSON.stringify(auto);

  return (
    <main className={styles.main}>
      <header className={styles.encabezado}>
        <div className={styles.filaEncabezado}>
          <h1>Clasificación de automóviles</h1>
          <BotonTema className={styles.tema} />
        </div>
        <p>Perceptrón multicapa 6 → 32 → 16 → 4 · Car Evaluation (UCI)</p>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.columnas}>
        <section className={styles.ventana}>
          <h2 className={styles.titulo}>Auto</h2>
          <div className={styles.cuerpo}>
            {opciones ? (
              Object.entries(opciones).map(([atributo, valores]) => (
                <div key={atributo} className={styles.campo}>
                  <span className={styles.etiqueta}>{ETIQUETAS[atributo] ?? atributo}</span>
                  <div className={styles.segmentos} role="radiogroup" aria-label={atributo}>
                    {valores.map((valor) => (
                      <button
                        key={valor}
                        type="button"
                        role="radio"
                        aria-checked={auto[atributo] === valor}
                        className={auto[atributo] === valor ? styles.activo : undefined}
                        onClick={() => setAuto({ ...auto, [atributo]: valor })}
                      >
                        {valor}
                      </button>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <p className={styles.tenue}>Cargando atributos…</p>
            )}
          </div>
        </section>

        <section className={`${styles.ventana} ${styles.panelPrediccion}`}>
          <h2 className={styles.titulo}>
            Predicción de la red
            <span className={styles.estado} aria-live="polite">
              {calculando ? "calculando…" : prediccion && `${Math.round(respondido.ms)} ms`}
            </span>
          </h2>
          <div className={`${styles.cuerpo} ${calculando ? styles.calculando : ""}`}>
            {prediccion ? (
              <>
                <div className={styles.resultado}>
                  <span className={styles.clase}>{prediccion.clase}</span>
                  <span>{claseActual?.nombre}</span>
                </div>

                <h3 className={styles.subtitulo}>Salida softmax</h3>
                <ul className={styles.barras}>
                  {CLASES.map(({ id }) => {
                    const p = prediccion.probabilidades[id] ?? 0;
                    return (
                      <li key={id} className={id === prediccion.clase ? styles.ganadora : undefined}>
                        <span>{id}</span>
                        <span className={styles.pista}>
                          <span className={styles.relleno} style={{ width: `${p * 100}%` }} />
                        </span>
                        <span className={styles.valor}>{(p * 100).toFixed(1)}%</span>
                      </li>
                    );
                  })}
                </ul>

                <h3 className={`${styles.subtitulo} ${styles.soloAmplio}`}>Entrada codificada</h3>
                <ol className={`${styles.vector} ${styles.soloAmplio}`}>
                  {prediccion.entrada.map((v, i) => (
                    <li key={i} title={Object.keys(ETIQUETAS)[i]}>
                      {v}
                    </li>
                  ))}
                </ol>
              </>
            ) : (
              <p className={styles.tenue}>Esperando respuesta del backend…</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
