<!-- app.vue -->
<template>
  <div class="app">
    <Header />
    <NuxtPage />
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()

onMounted(() => {
  auth.init()
})
</script>

