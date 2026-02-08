<script setup>
import {onMounted, onUnmounted} from "vue";
onMounted(() => {
  document.body.classList.add("no-scroll");
});

onUnmounted(() => {
  document.body.classList.remove("no-scroll");
});
</script>
<template>
  <div class="greetings">
    <h1 class="pink">Welcome to CV GRAM</h1>
    <h3 class="pink">
      Congratulations, You somehow reached my project!
    </h3>
    <h4>
      This serves as an application in which people can get their cv rated by an AI,
      have a profile similar to Linkedin, search for other people based on
      their cv scores and important criteria in it.
    </h4>
    <h3 class="pink">
      How i came up with it?
    </h3>
    <h4>
      Me and a former university colleague tried building a tech startup focused on this, but we had different visions,
      so we split :(. My part of the work now became CVGram.
    </h4>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
