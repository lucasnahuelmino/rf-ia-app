<template>

  <div class="panel">

    <h3>
      Estado del Instrumento
    </h3>

    <div class="grid">

      <div class="card">

        <span class="label">
          Equipo
        </span>

        <span class="value">
          BB60C
        </span>

      </div>

      <div class="card">

        <span class="label">
          Estado
        </span>

        <span class="value success">
          Conectado
        </span>

      </div>

      <div class="card">

        <span class="label">
          Firmware
        </span>

        <span class="value">
          {{ firmware ?? "--" }}
        </span>

      </div>

      <div class="card">

        <span class="label">
          Serie
        </span>

        <span class="value">
          {{ serial ?? "--" }}
        </span>

      </div>

      <div class="card">

        <span class="label">
          Temperatura
        </span>

        <span class="value">
          {{ temperature?.toFixed?.(1) ?? "--" }} °C
        </span>

      </div>

      <div class="card">

        <span class="label">
          Voltaje USB
        </span>

        <span class="value">
          {{ voltage?.toFixed?.(2) ?? "--" }} V
        </span>

      </div>

      <div class="card">

        <span class="label">
          Corriente USB
        </span>

        <span class="value">
          {{ current ?? "--" }} mA
        </span>

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

  border-radius: var(--radius);

  border: 1px solid var(--sncte-border);

  box-shadow: var(--shadow);

  padding: 16px;

  margin-bottom: 15px;
}

.panel h3 {

  margin-top: 0;

  color: var(--sncte-blue-dark);
}

.grid {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(120px,1fr)
    );
  gap: 8px;
}

.card {
  padding: 8px;
  border-radius: 8px;
  background: #f6f9ff;
}

.label {

  display: block;

  color: #5a6a85;

  font-size: 12px;

  margin-bottom: 6px;

  text-transform: uppercase;
}

.value {

  color: var(--sncte-blue-dark);

  font-size: 20px;

  font-weight: 600;
}

.success {

  color: #198754;
}

</style>