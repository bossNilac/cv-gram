<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI } from '../../util/apis.js'

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

async function doRegister() {
  if (loading.value) {
    return
  }

  errorMsg.value = ''
  successMsg.value = ''
  loading.value = true

  try {
    const result = await authAPI.register(email.value, password.value)
    successMsg.value = `Account created for ${result.email}. Check your email to verify the account before logging in.`
  } catch (error) {
    errorMsg.value = error.message || 'Register failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppPageShell title="Register." subtitle="Create an account first, then verify your email so the protected CV tools can be used.">
    <form class="form-stack" @submit.prevent="doRegister">
      <label class="field-label">
        Email
        <input v-model="email" class="text-input" placeholder="name@example.com" type="email" />
      </label>

      <label class="field-label">
        Password
        <input v-model="password" class="text-input" placeholder="At least 8 characters" type="password" />
      </label>

      <div class="button-row">
        <button class="primary-button" type="submit">
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </div>

      <div class="muted">
        <p>Already have an account? <RouterLink to="/login">Login</RouterLink></p>
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
