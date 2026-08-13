<template>

  <div class="tools">

    <label>
      <input
        v-model="showMaxHold"
        type="checkbox"
      />
      Max Hold
    </label>

    <label>
      <input
        v-model="showAverage"
        type="checkbox"
      />
      Average
    </label>

    <button
      @click="$emit('clear')"
    >
      Clear
    </button>

  </div>

</template>

<script setup lang="ts">

const showMaxHold =
  defineModel<boolean>(
    "showMaxHold"
  )

const showAverage =
  defineModel<boolean>(
    "showAverage"
  )

defineEmits([
  "clear"
])

</script>

<style scoped>

.tools {

  display: flex;

  gap: 20px;

  margin-bottom: 10px;
}

</style>