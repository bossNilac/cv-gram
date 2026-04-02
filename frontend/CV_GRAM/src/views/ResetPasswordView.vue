<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI } from '../../util/apis.js'

const route = useRoute()
const router = useRouter()
const token = computed(() => route.query.token || route.params.token || '')

const newPassword = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

async function doReset() {
  if (loading.value) {
    return
  }

  errorMsg.value = ''
  successMsg.value = ''

  if (!token.value) {
    errorMsg.value = 'Missing reset token.'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    await authAPI.resetPassword(token.value, newPassword.value)
    successMsg.value = 'Password updated. Redirecting you to login...'
    newPassword.value = ''
    confirmPassword.value = ''
    window.setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (error) {
    errorMsg.value = error.message || 'Reset failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppPageShell title="New Password." subtitle="Finish the reset flow by setting a replacement password.">
    <form class="form-stack" @submit.prevent="doReset">
      <label class="field-label">
        New password
        <input v-model="newPassword" class="text-input" placeholder="At least 8 characters" type="password" />
      </label>

      <label class="field-label">
        Confirm password
        <input v-model="confirmPassword" class="text-input" placeholder="Repeat the password" type="password" />
      </label>

      <div class="button-row">
        <button class="primary-button" type="submit">
          {{ loading ? 'Updating...' : 'Update Password' }}
        </button>
      </div>

      <div class="muted">
        <RouterLink to="/login">Back to login</RouterLink>
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
