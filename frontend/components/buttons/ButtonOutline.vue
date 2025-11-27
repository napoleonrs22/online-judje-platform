<!-- frontend/components/buttons/ButtonOutline.vue -->
<template>
  <component
    :is="tag"
    :to="to"
    :type="type"
    :disabled="disabled"
    class="btn btn--outline"
    @click="$emit('click')"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
const props = defineProps<{ to?: string; type?: string; disabled?: boolean }>()
const tag = computed(() => props.to ? 'NuxtLink' : 'button')
</script>