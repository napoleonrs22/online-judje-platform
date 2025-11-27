<!-- frontend/components/auth/LoginForm.vue -->
<template>
  <form @submit.prevent="handleLogin" class="login-form">
    <FormInput
      v-model="form.email"
      label="Введите логин"
      type="text"
      placeholder="admin@example.com"
      required
      :disabled="auth.isLoading"
      autocomplete="username"
      :error="errors.email"
    />
    <FormInput
      v-model="form.password"
      label="Введите пароль"
      type="password"
      placeholder="••••••••"
      required
      :disabled="auth.isLoading"
      autocomplete="current-password"
      :error="errors.password"
    />
    <FormError v-if="auth.error" :message="auth.error" />
    <div class="login-links">
      <ButtonLink type="button">Забыли пароль?</ButtonLink>
      <ButtonLink to="/auth/register">Нет аккаунта? Зарегистрироваться</ButtonLink>
    </div>
    <ButtonPrimary type="submit" :disabled="auth.isLoading">
      {{ auth.isLoading ? 'Вход...' : 'Вход' }}
    </ButtonPrimary>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter } from 'vue-router'
import FormInput from '~/components/forms/FormInput.vue'
import FormError from '~/components/forms/FormError.vue'
import ButtonPrimary from '~/components/buttons/ButtonPrimary.vue'
import ButtonLink from '~/components/buttons/ButtonLink.vue'
import useForm from '~/composables/useForm'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ email: '', password: '' })
const { errors, validate } = useForm(form, {
  email: (val) => val.includes('@') ? '' : 'Некорректный email',
  password: (val) => val.length >= 6 ? '' : 'Пароль минимум 6 символов'
})

const handleLogin = async () => {
  if (!validate()) return
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/problems')
  } catch {}
}
</script>