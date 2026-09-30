// Proxy hacia el backend: el navegador solo habla con Next.js y Next.js reenvía
// /api/* a FastAPI. En Docker el backend vive en la red interna (no expuesto).
import type { NextRequest } from "next/server";

// Se lee en tiempo de ejecución, así la misma imagen sirve en cualquier entorno
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

// Solo se reenvían los endpoints que usa la app (nada de /docs ni rutas con "..")
const PERMITIDAS = new Set(["opciones", "predecir"]);

async function reenviar(req: NextRequest, ctx: RouteContext<"/api/[...ruta]">) {
  const { ruta } = await ctx.params;
  if (ruta.length !== 1 || !PERMITIDAS.has(ruta[0])) {
    return Response.json({ detail: "No encontrado" }, { status: 404 });
  }
  try {
    const respuesta = await fetch(`${BACKEND_URL}/api/${ruta[0]}`, {
      method: req.method,
      headers: { "Content-Type": "application/json" },
      body: req.method === "POST" ? await req.text() : undefined,
      cache: "no-store",
    });
    return new Response(respuesta.body, {
      status: respuesta.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json({ detail: "Backend no disponible" }, { status: 502 });
  }
}

export { reenviar as GET, reenviar as POST };
