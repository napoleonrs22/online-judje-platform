<!-- frontend/components/auth/RegisterForm.vue -->
<template>
  <form @submit.prevent="handleRegister" class="login-form">
    <RoleSelector v-model="form.role" :disabled="auth.isLoading" />
    <FormInput
      v-model="form.username"
      label="Придумайте имя пользователя"
      type="text"
      required
      :disabled="auth.isLoading"
      autocomplete="username"
      :error="errors.username"
    />
    <FormInput
      v-model="form.email"
      label="Введите электронную почту"
      type="email"
      required
      :disabled="auth.isLoading"
      autocomplete="email"
      :error="errors.email"
    />
    <FormInput
      v-model="form.full_name"
      label="Введите полное имя"
      type="text"
      required
      :disabled="auth.isLoading"
      autocomplete="name"
      :error="errors.full_name"
    />
    <FormInput
      v-model="form.password"
      label="Придумайте пароль"
      type="password"
      required
      :disabled="auth.isLoading"
      autocomplete="new-password"
      :error="errors.password"
    />
    <FormInput
      v-model="form.password2"
      label="Повторите пароль"
      type="password"
      required
      :disabled="auth.isLoading"
      :error="errors.password2"
    />
    <FormError v-if="auth.error" :message="auth.error" />
    <ButtonPrimary type="submit" :disabled="auth.isLoading || passwordMismatch">
      {{ auth.isLoading ? 'Создание...' : 'Создать аккаунт' }}
    </ButtonPrimary>
    <div class="auth-links">
      <ButtonLink to="/auth/login">Уже есть аккаунт? Войти</ButtonLink>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter } from 'vue-router'
import FormInput from '~/components/forms/FormInput.vue'
import FormError from '~/components/forms/FormError.vue'
import RoleSelector from '~/components/forms/RoleSelector.vue'
import ButtonPrimary from '~/components/buttons/ButtonPrimary.vue'
import ButtonLink from '~/components/buttons/ButtonLink.vue'
import useForm from '~/composables/useForm'

const auth = useAuthStore()
const router = useRouter()

const form = ref({
  role: 'student',
  username: '',
  email: '',
  full_name: '',
  password: '',
  password2: ''
})

const { errors, validate } = useForm(form, {
  username: (val) => val.length >= 3 ? '' : 'Минимум 3 символа',
  email: (val) => val.includes('@') ? '' : 'Некорректный email',
  full_name: (val) => val.length >= 2 ? '' : 'Минимум 2 символа',
  password: (val) => val.length >= 6 ? '' : 'Минимум 6 символов',
  password2: (val, form) => val === form.password ? '' : 'Пароли не совпадают'
})

const passwordMismatch = computed(() => !!errors.value.password2)

const handleRegister = async () => {
  if (!validate()) return
  try {
    await auth.register(form.value)
    router.push('/problems')
  } catch {}
}
</script>