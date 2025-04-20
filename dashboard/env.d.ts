/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_PROMETHEUS_URL: string
    readonly VITE_ROBOT_API_URL: string
    readonly VITE_LOG_API_URL: string
    // add more env variables as needed
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }