import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // URL del API Gateway generada por CDK en ministack
  // Formato path-based para evitar problemas de DNS en Docker:
  // http://<ministack-ip>:4566/_aws/execute-api/<api-id>/$default
  const apigwBase = env.VITE_APIGW_BASE_URL || 'http://10.0.2.20:4566/_aws/execute-api/3d70b625/$default'

  // Fallback al backend FastAPI local si no hay API Gateway
  const fastapiTarget = env.VITE_API_PROXY_TARGET || 'http://localhost:8000'

  // Usa API Gateway si está configurado, si no cae al FastAPI local
  const useApigw = !!env.VITE_APIGW_BASE_URL || true

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: useApigw
        ? {
            // Proxy con rewrite → API Gateway path-based
            '/ecommerce': {
              target: `http://10.0.2.20:4566`,
              changeOrigin: true,
              rewrite: (path) =>
                `/_aws/execute-api/3d70b625/$default${path}`,
            },
            '/products': {
              target: `http://10.0.2.20:4566`,
              changeOrigin: true,
              rewrite: (path) =>
                `/_aws/execute-api/3d70b625/$default${path}`,
            },
          }
        : {
            // Modo fallback: FastAPI local
            '/ecommerce': { target: fastapiTarget, changeOrigin: true },
            '/products':  { target: fastapiTarget, changeOrigin: true },
            '/docs':      { target: fastapiTarget, changeOrigin: true },
            '/redoc':     { target: fastapiTarget, changeOrigin: true },
          },
    },
  }
})