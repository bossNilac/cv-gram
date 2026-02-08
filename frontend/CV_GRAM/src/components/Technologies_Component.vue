<script setup>
import TechnologiesItem from './Technologies_Item.vue'
import IconDatabase from './icons/IconDatabase.vue'
import IconSecurity from './icons/IconSecurity.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import IconSpecialFeatures from './icons/IconSpecialFeatures.vue'
import SupportIcon from './icons/IconSupport.vue'
</script>

<template>
  <TechnologiesItem>
    <template #icon>
      <SupportIcon />
    </template>
    <template #heading>Technologies and Stack</template>
    Built with <a>Python 3.13</a> (backend), <a>Vue.js</a> (frontend), and <a>PostgreSql</a> (database).
    Version control is handled with <a>git</a>, and selected features use the <a>OpenAI Api</a>.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconDatabase />
    </template>
    <template #heading>Database</template>
    <a>PostgreSql</a> was chosen for stability and flexibility. The schema combines relational
    data with <a>JSONB</a> for profile storage and supports full-text <a>searching</a> via
    <a>ts_vector</a>.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconSecurity />
    </template>
    <template #heading>Backend Security</template>
    Security is based on <a>cookies</a> and <a>SHA-256</a> hashing with session validation via
    user <a>uuid</a>. <a>Passwords</a> are encrypted using <a>argon2</a>, and all endpoints are
    <a>rate limited</a>.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Frontend</template>
    The frontend is built with <a>Vue.js</a> for its lightweight architecture and development
    flexibility.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconSpecialFeatures />
    </template>
    <template #heading>Special Features</template>
    The <a>OpenAi API</a> is used to experiment with advanced CV processing, powering
    <a>CV Rating</a> and <a>PDF to Linkedin</a> features.
  </TechnologiesItem>
</template>
