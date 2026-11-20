<template>

  <header class="header">

    <div class="title-container">
      <h1>SNCTE</h1>
      <h2>Sistema Nacional de Comprobación Técnica de Emisiones</h2>
      <h3>Monitoreo y Análisis del Espectro Radioeléctrico</h3>
    </div>

    <div class="logo-container">
      <img src="/enacom-logo.png" alt="ENACOM" />
    </div>

  </header>

</template>

<style scoped>

.header {
  background: var(--bg-panel);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 10px;
  border-bottom: 1px solid var(--border);
  height: 36px;
}

.title-container {
  display: flex;
  flex-direction: column;
}

.logo-container img {
  height: 24px;
  width: auto;
  object-fit: contain;
  opacity: 0.85;
}

h1 {
  margin: 0;
  color: var(--accent);
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 1px;
}

h2 {
  margin: 1px 0 0 0;
  color: var(--text-muted);
  font-size: 8px;
  font-weight: 500;
}

h3 {
  margin: 0;
  color: var(--text-muted);
  font-size: 7px;
  font-weight: 400;
}

</style>