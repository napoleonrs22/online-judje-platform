<!-- frontend/components/forms/FormError.vue -->
<template>
  <div class="auth-error">
    {{ message }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>