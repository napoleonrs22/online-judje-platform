// frontend/composables/useAuth.ts
import { useAuthStore } from '~/stores/auth'

export default function useAuth() {
  const auth = useAuthStore()
  return auth
}