import { fileURLToPath, URL } from 'node:url'
import process from 'node:process'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBaseUrl = env.VITE_API_BASE_URL || ''
  const apiProxyTarget =
    env.VITE_API_PROXY_TARGET || apiBaseUrl.replace(/\/api\/?$/, '').replace(/\/$/, '')
  const proxyHeaders = apiProxyTarget.includes('ngrok')
    ? { 'ngrok-skip-browser-warning': 'true' }
    : undefined

  return {
    // Strip console/debugger statements from production builds.
    esbuild: {
      drop: mode === 'production' ? ['console', 'debugger'] : [],
    },
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      allowedHosts: true,
      ...(apiProxyTarget
        ? {
            proxy: {
              '/api': {
                target: apiProxyTarget,
                changeOrigin: true,
                secure: false,
                headers: proxyHeaders,
              },
            },
          }
        : {}),
    },
  }
})
