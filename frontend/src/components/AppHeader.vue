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

    /enacom-logo.png alt="ENACOM"
      class="logo"
    />

  </header>

</template>

<style scoped>

.header {

  background: white;

  display: flex;

  justify-content: space-between;

  align-items: center;

  padding: 20px 30px;

  border-radius: var(--radius);

  box-shadow: var(--shadow);

  margin-bottom: 20px;
}

.title-container {

  display: flex;

  flex-direction: column;
}

.logo {

  height: 90px;

  object-fit: contain;
}

h1 {

  margin: 0;

  color: var(--sncte-blue-dark);

  font-size: 38px;

  font-weight: 700;

  line-height: 1;
}

h2 {

  margin: 8px 0 0 0;

  color: var(--sncte-blue);

  font-size: 15px;

  font-weight: 600;
}

h3 {

  margin: 4px 0 0 0;

  color: #65748b;

  font-size: 13px;

  font-weight: 400;
}

</style>