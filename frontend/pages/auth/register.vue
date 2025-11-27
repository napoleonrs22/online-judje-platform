<!-- pages/auth/register.vue -->
<template>
  <AuthLayout title="Регистрация аккаунта">
    <RegisterForm />
  </AuthLayout>
</template>

<script setup>
import AuthLayout from '~/components/auth/AuthLayout.vue'
import RegisterForm from '~/components/auth/RegisterForm.vue'
</script>