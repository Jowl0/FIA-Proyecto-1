"use client";

import { useSyncExternalStore } from "react";

type Tema = "claro" | "oscuro";

const CONSULTA_OSCURO = "(prefers-color-scheme: dark)";

// Tema efectivo: el elegido con el botón o, si no hay, el del sistema
function temaActual(): Tema {
  const elegido = document.documentElement.dataset.tema;
  if (elegido === "claro" || elegido === "oscuro") return elegido;
  return matchMedia(CONSULTA_OSCURO).matches ? "oscuro" : "claro";
}

// Se vuelve a leer si cambia el tema del sistema o el atributo data-tema
function suscribir(avisar: () => void) {
  const sistema = matchMedia(CONSULTA_OSCURO);
  sistema.addEventListener("change", avisar);
  const observador = new MutationObserver(avisar);
  observador.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-tema"],
  });
  return () => {
    sistema.removeEventListener("change", avisar);
    observador.disconnect();
  };
}

function aplicarTema(tema: Tema) {
  document.documentElement.dataset.tema = tema;
  try {
    localStorage.setItem("tema", tema);
  } catch {}
}

// Transición: el tema nuevo aparece como un círculo que crece desde el botón.
// Sin soporte de View Transitions o con "reducir movimiento", cambia al instante.
function cambiarTema(tema: Tema, boton: HTMLElement) {
  const sinAnimacion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!document.startViewTransition || sinAnimacion) {
    aplicarTema(tema);
    return;
  }

  const { left, top, width, height } = boton.getBoundingClientRect();
  const x = left + width / 2;
  const y = top + height / 2;
  // Radio hasta la esquina más lejana de la ventana
  const radio = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));

  const transicion = document.startViewTransition(() => aplicarTema(tema));
  transicion.ready.then(() => {
    document.documentElement.animate(
      { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radio}px at ${x}px ${y}px)`] },
      { duration: 550, easing: "cubic-bezier(0.4, 0, 0.2, 1)", pseudoElement: "::view-transition-new(root)" },
    );
  });
}

export default function BotonTema({ className }: { className?: string }) {
  // En el servidor no se conoce el tema: el botón aparece al hidratar
  const tema = useSyncExternalStore(suscribir, temaActual, () => null);
  if (tema === null) return null;

  const siguiente: Tema = tema === "oscuro" ? "claro" : "oscuro";
  return (
    <button
      type="button"
      className={className}
      aria-label={`Cambiar a modo ${siguiente}`}
      onClick={(evento) => cambiarTema(siguiente, evento.currentTarget)}
    >
      {siguiente === "oscuro" ? "modo oscuro" : "modo claro"}
    </button>
  );
}
