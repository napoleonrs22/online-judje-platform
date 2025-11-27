<!-- pages/auth/login.vue -->
<template>
  <AuthLayout title="Авторизация в аккаунт">
    <LoginForm />
  </AuthLayout>
</template>

<script setup>
import AuthLayout from '~/components/auth/AuthLayout.vue'
import LoginForm from '~/components/auth/LoginForm.vue'
</script>