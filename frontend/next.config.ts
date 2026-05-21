import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_JAVA_URL: process.env.NEXT_PUBLIC_JAVA_URL || "http://localhost:8080",
    NEXT_PUBLIC_PYTHON_URL: process.env.NEXT_PUBLIC_PYTHON_URL || "http://localhost:8000",
  },
};

export default nextConfig;
