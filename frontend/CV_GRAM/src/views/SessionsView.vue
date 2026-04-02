<script setup>
import { onMounted, ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI } from '../../util/apis.js'
import { formatDateTime } from '@/utils/formatters.js'

const loading = ref(true)
const errorMsg = ref('')
const successMsg = ref('')
const sessions = ref([])

async function loadSessions() {
  loading.value = true
  errorMsg.value = ''

  try {
    const response = await authAPI.getSessions()
    sessions.value = Array.isArray(response) ? response : []
  } catch (error) {
    errorMsg.value = error.message || 'Failed to load sessions'
  } finally {
    loading.value = false
  }
}

async function revokeSession(sessionId) {
  successMsg.value = ''
  errorMsg.value = ''

  try {
    await authAPI.deleteSession(sessionId)
    successMsg.value = 'Session revoked.'
    await loadSessions()
  } catch (error) {
    errorMsg.value = error.message || 'Failed to revoke session'
  }
}

async function revokeAll() {
  successMsg.value = ''
  errorMsg.value = ''

  try {
    await authAPI.logoutAll()
  } catch (error) {
    errorMsg.value = error.message || 'Failed to revoke all sessions'
  }
}

onMounted(() => {
  loadSessions()
})
</script>

<template>
  <AppPageShell title="Sessions." subtitle="Inspect the active cookie sessions recorded by the backend.">
    <AppNav />

    <div class="button-row">
      <button class="secondary-button" type="button" @click="loadSessions">Refresh list</button>
      <button class="danger-button" type="button" @click="revokeAll">Sign out everywhere</button>
    </div>

    <div v-if="successMsg" class="status-message success">{{ successMsg }}</div>
    <div v-if="errorMsg" class="status-message error">{{ errorMsg }}</div>
    <div v-if="loading" class="status-message success">Loading sessions...</div>

    <div v-else class="stack-list">
      <article v-for="session in sessions" :key="session.id" class="list-card">
        <h2>{{ session.agent || 'Unknown agent' }}</h2>
        <p><strong>Session ID:</strong> {{ session.id }}</p>
        <p><strong>IP:</strong> {{ session.ip }}</p>
        <p><strong>Created:</strong> {{ formatDateTime(session.created_at) }}</p>
        <p><strong>Expires:</strong> {{ formatDateTime(session.expires_at) }}</p>
        <div class="button-row">
          <button class="danger-button" type="button" @click="revokeSession(session.id)">Sign out this device</button>
        </div>
      </article>

      <p v-if="sessions.length === 0" class="muted">No active sessions were returned.</p>
    </div>
  </AppPageShell>
</template>
