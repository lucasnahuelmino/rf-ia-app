<template>

  <header class="header">

    <div>

      <h1>
        SNCTE
      </h1>

      <h2>
        Sistema Nacional de Comprobación Técnica de Emisiones
      </h2>

    </div>

    /enacom-logo.png

  </header>

</template>

<style scoped>

.header {

  background: white;

  display: flex;

  justify-content: space-between;

  align-items: center;

  padding: 20px;

  box-shadow: var(--shadow);

  border-radius: var(--radius);

  margin-bottom: 20px;
}

.logo {

  height: 80px;
}

h1 {

  margin: 0;

  color: var(--sncte-blue-dark);

  font-size: 36px;
}

h2 {

  margin: 4px 0 0 0;

  color: var(--sncte-blue);

  font-size: 15px;

  font-weight: normal;
}

</style>
