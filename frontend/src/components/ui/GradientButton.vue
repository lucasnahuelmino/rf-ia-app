<template>
  <button class="gradient-button" :class="{ active }">
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{ active?: boolean }>()
</script>

<style scoped>
.gradient-button {
  flex: 1;
  min-width: 70px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 2px 8px rgba(59,130,246,0.3);
}

.gradient-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59,130,246,0.4);
}

.gradient-button.active {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  box-shadow: 0 0 0 2px rgba(139,92,246,0.5);
}
</style>