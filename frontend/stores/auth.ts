// stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>('')
  const user = ref<any>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string>('')

  const isLoggedIn = computed(() => !!token.value)
  const isStudent = () => user.value?.role === 'student'
  const isTeacher = () => user.value?.role === 'teacher'

  // === ВХОД ===
  async function login(email: string, password: string) {
    isLoading.value = true
    error.value = ''
    try {
      const res = await $fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: { email: email.trim().toLowerCase(), password }
      })

      token.value = res.access_token
      const tokenCookie = useCookie('token', { maxAge: 60 * 60 * 24 * 7 })
      tokenCookie.value = token.value

      await loadUser()
      navigateTo('/problems')
    } catch (e: any) {
      handleError(e, 'Ошибка входа')
      throw error.value
    } finally {
      isLoading.value = false
    }
  }

  // === РЕГИСТРАЦИЯ ===
  async function register(data: {
    username: string
    email: string
    full_name: string
    password: string
    role: 'student' | 'teacher'
  }) {
    isLoading.value = true
    error.value = ''
    try {
      const res = await $fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: {
          username: data.username.trim().toLowerCase(),
          email: data.email.trim().toLowerCase(),
          full_name: data.full_name.trim(),
          password: data.password,
          role: data.role
        }
      })

      // Автологин после регистрации
      await login(data.email, data.password)
    } catch (e: any) {
      handleError(e, 'Ошибка регистрации')
      throw error.value
    } finally {
      isLoading.value = false
    }
  }

  // === ЗАГРУЗКА ПОЛЬЗОВАТЕЛЯ ===
  async function loadUser() {
    if (!token.value) return
    try {
      user.value = await $fetch('http://localhost:8000/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
    } catch (e) {
      console.error('Не удалось загрузить пользователя')
      logout() // если токен протух — выкидываем
    }
  }

  // === ИНИЦИАЛИЗАЦИЯ ПРИ СТАРТЕ ===
  async function init() {
    const tokenCookie = useCookie('token')
    if (tokenCookie.value) {
      token.value = tokenCookie.value
      await loadUser()
    }
  }

  // === ВЫХОД — САМОЕ ГЛАВНОЕ! ===
  async function logout() {
      console.log('Выход начат...') // ← УВИДИШЬ В КОНСОЛИ

      try {
        if (token.value) {
          await $fetch('http://localhost:8000/api/auth/logout', {
            method: 'POST',
            headers: { Authorization: `Bearer ${token.value}` }
          })
          console.log('Сервер подтвердил выход')
        }
      } catch (err) {
        console.warn('Сервер не ответил на logout — чистим локально')
      } finally {
        token.value = ''
        user.value = null
        useCookie('token').value = null

        console.log('Токен удалён, переходим на главную')

        // ВРЕМЕННО — чтобы точно увидеть, что сработало
        alert('Вы успешно вышли!')

        await navigateTo('/')
      }
    }

  // Вспомогательная функция обработки ошибок
  function handleError(e: any, defaultMsg: string) {
    console.error(defaultMsg + ':', e)
    if (e.status === 422 && e.data?.detail) {
      if (Array.isArray(e.data.detail)) {
        error.value = e.data.detail.map((err: any) => `${err.loc?.[1] || 'поле'}: ${err.msg}`).join('; ')
      } else {
        error.value = e.data.detail
      }
    } else if (e.message) {
      error.value = e.message
    } else {
      error.value = defaultMsg
    }
  }

  return {
    token,
    user,
    isLoading,
    error,
    isLoggedIn,
    isStudent,
    isTeacher,
    login,
    register,
    loadUser,
    init,
    logout
  }
})