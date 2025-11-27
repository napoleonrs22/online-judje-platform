// plugins/auth.client.ts
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.init()
})