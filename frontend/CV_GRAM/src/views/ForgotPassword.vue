<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI } from '../../util/apis.js'

const email = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

async function requestReset() {
  if (loading.value) {
    return
  }

  errorMsg.value = ''
  successMsg.value = ''
  loading.value = true

  try {
    await authAPI.forgotPassword(email.value)
    successMsg.value = 'If the address exists, a reset email has been sent.'
  } catch (error) {
    errorMsg.value = error.message || 'Password reset failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppPageShell title="Reset." subtitle="Request a password reset link for an existing account.">
    <form class="form-stack" @submit.prevent="requestReset">
      <label class="field-label">
        Email
        <input v-model="email" class="text-input" placeholder="name@example.com" type="email" />
      </label>

      <div class="button-row">
        <button class="primary-button" type="submit">
          {{ loading ? 'Sending...' : 'Reset Password' }}
        </button>
      </div>

      <div class="muted">
        <p>No account? <RouterLink to="/register">Register</RouterLink></p>
        <p>Remembered it? <RouterLink to="/login">Login</RouterLink></p>
      </div>

      <div v-if="successMsg" class="status-message success">
        {{ successMsg }}
      </div>

      <div v-if="errorMsg" class="status-message error">
        {{ errorMsg }}
      </div>
    </form>
  </AppPageShell>
</template>
