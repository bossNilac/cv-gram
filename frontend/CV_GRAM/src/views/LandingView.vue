<script setup>
import WelcomeScreen from '@/components/WelcomeScreen.vue'
import TechnologiesComponent from '@/components/Technologies_Component.vue'
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="landing-layout">
    <header>
      <img alt="App logo" class="logo" src="@/assets/logo.svg" width="200" height="300" />

      <div class="wrapper">
        <WelcomeScreen />

        <nav>
          <a href="https://github.com">Github</a>
          <RouterLink to="/login">Login</RouterLink>
          <RouterLink to="/register">Register</RouterLink>
        </nav>
      </div>
    </header>

    <main>
      <TechnologiesComponent />
    </main>
  </section>
</template>

<style scoped>
.landing-layout {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color:  hsla(340, 76%, 54%, 1);;
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  .landing-layout {
    min-height: 100vh;
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    align-items: center;
    gap: 2.5rem;
    padding: 0 3rem;
  }

  header {
    display: flex;
    place-items: center;
    padding-right: 1rem;
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;
    padding: 1rem 0;
    margin-top: 1rem;
  }

  main {
    min-width: 0;
  }
}
</style>
