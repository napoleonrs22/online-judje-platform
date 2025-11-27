<!-- components/auth/AuthLayout.vue -->
<template>
  <div class="auth-wrapper">
    <!-- Левая часть — белая карточка -->
    <div class="auth-left">
      <div class="auth-card">
        <h1 class="auth-title">{{ title }}</h1>
        <slot />
      </div>
    </div>

    <!-- Правая часть — фон с кодом -->
    <div class="auth-right" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #000;
}

.auth-left {
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 3rem 2.5rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.auth-title {
  font-size: 2.4rem;
  font-weight: 700;
  color: #111;
  text-align: center;
  margin-bottom: 2.5rem;
}

.auth-right {
  background: url('/chris-ried-ieic5Tq8YMk-unsplash.jpg') center/cover no-repeat;
  position: relative;
}

.auth-right::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0,0,0,0.85), rgba(10,0,40,0.95));
}

/* Мобильная версия — карточка по центру */
@media (max-width: 968px) {
  .auth-wrapper {
    grid-template-columns: 1fr;
  }
  .auth-right {
    display: none;
  }
  .auth-left {
    background: white;
    min-height: 100vh;
  }
}
</style>