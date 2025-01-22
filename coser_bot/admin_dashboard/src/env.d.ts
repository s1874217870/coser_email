/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_JWT_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
