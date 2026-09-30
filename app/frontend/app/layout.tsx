import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import { headers } from "next/headers";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
});

const TITULO = "Clasificación de automóviles · Red neuronal";
const DESCRIPCION =
  "Elige las características de un auto y una red neuronal (perceptrón multicapa) " +
  "entrenada con el conjunto Car Evaluation de la UCI lo clasifica en tiempo real " +
  "como inaceptable, aceptable, bueno o muy bueno.";

// Las redes sociales necesitan URLs absolutas para la imagen de vista previa.
// Se arma con el dominio por el que llegó la petición (p. ej. el del túnel de
// Cloudflare), así funciona sin configurar la URL pública de antemano.
export async function generateMetadata(): Promise<Metadata> {
  const h = await headers();
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:3000";
  const protocolo = h.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");

  return {
    metadataBase: new URL(`${protocolo}://${host}`),
    title: TITULO,
    description: DESCRIPCION,
    openGraph: {
      title: TITULO,
      description: DESCRIPCION,
      type: "website",
      locale: "es_MX",
      siteName: "Proyecto 1 · Fundamentos de Inteligencia Artificial",
    },
    twitter: {
      card: "summary_large_image",
      title: TITULO,
      description: DESCRIPCION,
    },
  };
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // suppressHydrationWarning: el script de abajo pone data-tema antes de React
    <html lang="es" className={jetbrainsMono.className} suppressHydrationWarning>
      <head>
        {/* Aplica el tema guardado antes de pintar, para que no parpadee */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var t=localStorage.getItem("tema");if(t)document.documentElement.dataset.tema=t}catch(e){}`,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
