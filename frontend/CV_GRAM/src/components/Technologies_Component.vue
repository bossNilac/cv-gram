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
    This project was built using <a>Python 3.13</a>(backend), <a>Vue.js</a>(frontend), <a>PostgreSql</a>(database).
    To ensure version control I used <a>git</a> and for special feature implementation I used
    <a>OpenAI Api</a>.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconDatabase />
    </template>
    <template #heading>Database</template>
    I chose
    <a>PostgreSql</a>
    because of its stability, functionality and ease of database development. In this part of the project I implemented
    a relational schema that contains <a>JSONB</a> for flexible profile storage and some database functions such as <a>searching</a> using
    <a>ts_vector</a>.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconSecurity />
    </template>
    <template #heading>Backend Security</template>
    To ensure users security I implemented a <a>cookies</a> system along side the <a>SHA-256</a> hashing algorithm to ensure the cryptographic security
    of them. Alongside this, I also chose a sessions system in which cookies get revoked,
    expire and get verified against the database by checking the <a>uuid</a> of each user which
    is encapsulated in the cookie.Each session gets checked in the appropriate API paths.
    <a>Passwords</a> get encrypted using the <a>argon2</a> algorithm making sure that they are
    secure and hard to crack in case of a database leak.
    Finally, all the API endpoints are <a>rate limited</a> meaning important endpoints cannot get spammed.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Frontend</template>
    The frontend for this application is done using the <a>Vue.js</a> framework because of
    its lightweight, flexibility and ease of developing inside it.
  </TechnologiesItem>

  <TechnologiesItem>
    <template #icon>
      <IconSpecialFeatures />
    </template>
    <template #heading>Special Features</template>
    In this project I experimented with <a>OpenAi API</a> in order to create a novel
    approach to CV handling. This technology powers the <a>CV Rating</a>
    mechanism, as well as the <a>PDF TO Linkedin</a> functionality.
  </TechnologiesItem>

</template>
