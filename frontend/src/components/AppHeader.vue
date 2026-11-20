<template>

  <header class="header">

    <div class="title-container">

      <h1>
        SNCTE
      </h1>

      <h2>
        Sistema Nacional de Comprobación Técnica de Emisiones
      </h2>

      <h3>
        Monitoreo y Análisis del Espectro Radioeléctrico
      </h3>

    </div>

    <div class="logo-container">
      <img src="/enacom-logo.png" alt="ENACOM" />
    </div>

  </header>

</template>

<style scoped>

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  margin-bottom: 4px;
  height: 48px;
}

.title-container {
  display: flex;
  flex-direction: column;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-container img {
  height: 32px;
  width: auto;
  object-fit: contain;
}

h1 {
  margin: 0;
  color: var(--sncte-blue-dark);
  font-size: 18px;
  font-weight: 600;
  line-height: 1;
}

h2 {
  margin: 2px 0 0 0;
  color: var(--sncte-blue);
  font-size: 9px;
  font-weight: 600;
}

h3 {
  margin: 1px 0 0 0;
  color: #65748b;
  font-size: 8px;
  font-weight: 400;
}

</style>