<template>

  <div class="preset-selector">

    <label>

      <span>Categoría</span>

      <select v-model="categoria">

        <option
          v-for="item in categorias"
          :key="item"
        >
          {{ item }}
        </option>

      </select>

    </label>

    <label>

      <span>Preset RF</span>

      <select
        v-model="preset"
        @change="loadPreset"
      >

        <option
          value=""
        >
          Seleccionar...
        </option>

        <option
          v-for="item in presets"
          :key="item.nombre"
          :value="item.nombre"
        >

          {{ item.nombre }}

        </option>

      </select>

    </label>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  ref,
} from "vue"

import {
  PRESETS_RF,
} from "../data/presetsRF"

const emit = defineEmits([
  "presetLoaded",
])

const categorias =
  Object.keys(
    PRESETS_RF
  )

const categoria =
  ref<string>(
    categorias[0] ?? ""
  )

const preset =
  ref("")

const presets = computed(
  () =>
    PRESETS_RF[
      categoria.value as keyof typeof PRESETS_RF
    ] ?? []
)

function loadPreset() {

  const selected =
    presets.value.find(
      p =>
        p.nombre === preset.value
    )

  if (!selected)
    return

  emit(
    "presetLoaded",
    selected
  )
}

</script>
<style scoped>

.preset-selector {

  display: flex;

  flex-direction: column;

  gap: 10px;

  margin-bottom: 12px;
}

label {

  display: flex;

  flex-direction: column;

  gap: 4px;
}

span {

  font-size: 11px;

  font-weight: 600;

  color: var(--sncte-blue-dark);
}

select {

  height: 30px;

  padding: 0 8px;

  font-size: 12px;

  background: white;

  border: 1px solid var(--sncte-border);

  border-radius: 6px;
}

</style>