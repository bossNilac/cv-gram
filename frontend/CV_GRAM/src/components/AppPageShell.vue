<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <main class="app-page">
    <section class="page-panel">
      <div class="page-brand">
        <img alt="CV GRAM logo" class="brand-logo" src="@/assets/logo.svg" width="84" height="84" />
        <div>
          <p class="eyebrow">CV GRAM</p>
          <h1 class="page-title">{{ title }}</h1>
          <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        </div>
      </div>

      <slot />
    </section>
  </main>
</template>
