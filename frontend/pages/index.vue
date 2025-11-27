<!-- frontend/pages/index.vue -->
<template>
  <main class="hero">
    <div class="hero__code-bg"></div>
    <div class="container hero__content">
      <h2 class="hero__title">Платформа<br>для программистов</h2>
      <p class="hero__subtitle">Решай задачи, развивайся, побеждай!</p>
      <ButtonPrimary to="/problems" class="hero__btn">Начать</ButtonPrimary>
    </div>
  </main>
</template>

<script setup lang="ts">
import ButtonPrimary from '~/components/buttons/ButtonPrimary.vue'
</script>