<!-- frontend/components/common/Header.vue -->
<template>
  <header class="header">
    <div class="container header__inner">
      <!-- Логотип — кликабельный -->
      <NuxtLink to="/" class="header__logo">
        CodeContest
      </NuxtLink>

      <nav class="header__nav">
        <!-- Не авторизован -->
        <template v-if="!auth.isLoggedIn">
          <NuxtLink to="/auth/login" class="btn-outline">
            Войти
          </NuxtLink>
          <NuxtLink to="/auth/register" class="btn-dark">
            Регистрация
          </NuxtLink>
        </template>

        <!-- Авторизован -->
        <template v-else>
          <span class="header__user">
            Привет, {{ auth.user?.username }}!
          </span>
          <button @click="auth.logout()" class="btn-outline">
            Выйти
          </button>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.header {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 1.8rem 0;
  z-index: 1000;
  pointer-events: none;
}

.header__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  pointer-events: auto;
}

.header__logo {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  text-decoration: none;
  letter-spacing: -1px;
}

/* Кнопки */
.btn-outline,
.btn-dark {
  padding: 10px 26px;
  border-radius: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
  display: inline-block;
}

.btn-outline {
  border: 2px solid rgba(255,255,255,0.35);
  color: white;
  background: transparent;
}

.btn-outline:hover {
  background: rgba(255,255,255,0.1);
  border-color: white;
}

.btn-dark {
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
  backdrop-filter: blur(8px);
}

.btn-dark:hover {
  background: rgba(255,255,255,0.25);
}

.header__user {
  color: white;
  margin-right: 1rem;
  font-weight: 500;
}
</style>