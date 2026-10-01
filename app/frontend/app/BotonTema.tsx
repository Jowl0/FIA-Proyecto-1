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

// Transición: fundido parejo entre el tema viejo y el nuevo (View Transitions).
// Sin soporte o con "reducir movimiento", cambia al instante.
function cambiarTema(tema: Tema) {
  const sinAnimacion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!document.startViewTransition || sinAnimacion) {
    aplicarTema(tema);
    return;
  }
  document.startViewTransition(() => aplicarTema(tema));
}

function Luna() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

function Sol() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
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
      title={`Modo ${siguiente}`}
      onClick={() => cambiarTema(siguiente)}
    >
      {siguiente === "oscuro" ? <Luna /> : <Sol />}
    </button>
  );
}
