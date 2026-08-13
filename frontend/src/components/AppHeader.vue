<template>

  <header class="header">

    <div class="branding">

      <img
        src="/enacom-logo.png"
        alt="ENACOM"
        class="logo"
      />

      <div>

        <h1>
          SNCTE
        </h1>

        <h2>
          Sistema Nacional de Comprobación Técnica de Emisiones
        </h2>

      </div>

    </div>

  </header>

</template>

<style scoped>

.header {

  background: white;

  border-bottom: 3px solid var(--sncte-blue);

  padding: 15px 20px;

  margin-bottom: 15px;
}

.branding {

  display: flex;

  gap: 20px;

  align-items: center;
}

.logo {

  height: 70px;
}

h1 {

  margin: 0;

  color: var(--sncte-blue-dark);

  font-size: 32px;
}

h2 {

  margin: 4px 0 0 0;

  color: var(--sncte-blue);

  font-size: 15px;

  font-weight: normal;
}

</style>