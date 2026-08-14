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
    <img src= "/enacom-logo.png" alt="ENACOM">
    </div>  

  </header>

</template>

<style scoped>

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 10px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: 2px;
}

.title-container {
  display: flex;
  flex-direction: column;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content:center;
}

.logo {  
  height: 80px;
  width: auto;
  object-fit: contain;
}

h1 {
  margin: 0;
  color: var(--sncte-blue-dark);
  font-size: 35px;
  font-weight: 600;
  line-height: 1;
}

h2 {
  margin: 8px 0 0 0;
  color: var(--sncte-blue);
  font-size: 12px;
  font-weight: 600;
}

h3 {
  margin: 4px 0 0 0;
  color: #65748b;
  font-size: 11px;
  font-weight: 400;
}

</style>