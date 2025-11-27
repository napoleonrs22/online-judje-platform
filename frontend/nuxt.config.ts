// nuxt.config.ts
import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@pinia/nuxt'],

  // ЭТО ГЛАВНОЕ — АВТОИМПОРТ ВСЕХ КОМПОНЕНТОВ
  components: [
    '~/components',
    '~/components/auth',
    '~/components/buttons',
    '~/components/common',
    '~/components/forms'
  ],

  css: ['~/assets/scss/main.scss'],

  alias: {
    '~': fileURLToPath(new URL('./', import.meta.url)),
    '@': fileURLToPath(new URL('./', import.meta.url))
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL || 'http://localhost:8000/api'
    }
  }
})