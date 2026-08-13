<template>

  <div class="preset-panel">

    <h4>Presets RF</h4>

    <div class="grid">

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

        <span>Preset</span>

        <select
          v-model="preset"
        >

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

    <button
      @click="loadPreset"
    >
      Cargar Preset
    </button>

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
        p.nombre ===
        preset.value
    )

  if (!selected)
    return

  emit(
    "presetLoaded",
    selected,
  )
}

</script>

<style scoped>
.preset-panel {

  background: #f8fbff;

  border: 1px solid var(--sncte-border);

  border-radius: 12px;

  padding: 16px;

  margin-bottom: 16px;
}
</style>