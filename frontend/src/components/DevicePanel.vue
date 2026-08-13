<template>

  <div class="panel">

    <h3>
      Estado del Instrumento
    </h3>

    <div class="grid">

      <div>
        <b>Equipo</b>
        <span>BB60C</span>
      </div>

      <div>
        <b>Estado</b>
        <span>Conectado</span>
      </div>

      <div>
        <b>Firmware</b>
        <span>{{ firmware }}</span>
      </div>

      <div>
        <b>Serie</b>
        <span>{{ serial }}</span>
      </div>

      <div>
        <b>Temperatura</b>
        <span>{{ temperature }} °C</span>
      </div>

      <div>
        <b>USB</b>
        <span>{{ voltage }} V</span>
      </div>

      <div>
        <b>Corriente</b>
        <span>{{ current }} mA</span>
      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

defineProps({

  firmware: Number,

  serial: Number,

  temperature: Number,

  voltage: Number,

  current: Number,
})

</script>

<style scoped>

.panel {

  background: white;

  border: 1px solid var(--sncte-border);

  padding: 15px;

  margin-bottom: 15px;
}

.grid {

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(180px,1fr)
    );

  gap: 12px;
}

.grid div {

  display: flex;

  flex-direction: column;
}

.grid b {

  color: var(--sncte-blue-dark);
}

</style>