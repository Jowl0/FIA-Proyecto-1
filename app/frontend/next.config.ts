import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Servidor mínimo autocontenido para la imagen de Docker
  output: "standalone",
};

export default nextConfig;
