<template>
  <div class="gradient-button-group">
    <slot />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.gradient-button-group {
  display: flex;
  gap: 4px;
  padding: 6px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(168,85,247,0.15));
  border: 1px solid rgba(99,102,241,0.3);
}
</style>