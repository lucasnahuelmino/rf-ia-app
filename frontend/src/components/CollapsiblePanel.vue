<template>

  <details
    class="panel"
    :open="defaultOpen"
  >

    <summary>

      {{ title }}

    </summary>

    <div class="content">

      <slot />

    </div>

  </details>

</template>

<script setup lang="ts">

defineProps({

  title: String,

  defaultOpen: {
    type: Boolean,
    default: false,
  },
})

</script>

<style scoped>

.panel {

  background: white;

  border: 1px solid var(--sncte-border);

  border-radius: var(--radius);

  box-shadow: var(--shadow);

  margin-bottom: 12px;
}

summary {

  cursor: pointer;

  padding: 12px 16px;

  font-weight: 700;

  color: var(--sncte-blue-dark);

  user-select: none;
}

.content {
  padding: 1px 1px 10px 16px;
}

</style>