<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { authAPI } from '../../util/apis.js'

const isLoggingOut = ref(false)

async function handleLogout() {
  if (isLoggingOut.value) {
    return
  }

  isLoggingOut.value = true

  try {
    await authAPI.logout()
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<template>
  <nav class="dashboard-nav">
    <RouterLink to="/dashboard">Workspace</RouterLink>
    <RouterLink to="/score">CV Review</RouterLink>
    <RouterLink to="/profile">Profile</RouterLink>
    <RouterLink to="/search">Search</RouterLink>
    <RouterLink to="/sessions">Security</RouterLink>
    <button class="nav-button" type="button" @click="handleLogout">
      {{ isLoggingOut ? 'Signing out...' : 'Sign out' }}
    </button>
  </nav>
</template>
