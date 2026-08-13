<template>

  <div class="markers">

    <button
      @click="$emit('clear')"
    >
      Clear Markers
    </button>

  </div>

</template>

<script setup lang="ts">

defineEmits([
  "clear"
])

</script>