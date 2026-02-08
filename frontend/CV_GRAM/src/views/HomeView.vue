<script setup>
import TechnologiesComponent from '../components/Technologies_Component.vue'
import {onMounted, onUnmounted} from "vue";
onMounted(() => {
  document.body.classList.add("no-scroll");
});

onUnmounted(() => {
  document.body.classList.remove("no-scroll");
});
</script>

<template>
  <main>
    <TechnologiesComponent />
  </main>
</template>
