<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI } from '../../util/apis.js'

const route = useRoute()
const token = computed(() => route.query.token || route.params.token || '')
const status = ref('idle')
const message = ref('')

async function verifyEmail() {
  if (!token.value || status.value === 'loading') {
    if (!token.value) {
      status.value = 'error'
      message.value = 'Missing verification token.'
    }
    return
  }

  status.value = 'loading'
  message.value = ''

  try {
    await authAPI.verifyEmail(token.value)
    status.value = 'success'
    message.value = 'Email verified. You can log in now.'
  } catch (error) {
    status.value = 'error'
    message.value = error.message || 'Verification failed'
  }
}

onMounted(() => {
  verifyEmail()
})
</script>

<template>
  <AppPageShell title="Verify." subtitle="Confirm the email token that was sent during registration.">
    <div class="form-stack">
      <div v-if="status === 'loading'" class="status-message success">
        Verifying your email...
      </div>

      <div v-else-if="status === 'success'" class="status-message success">
        {{ message }}
      </div>

      <div v-else-if="status === 'error'" class="status-message error">
        {{ message }}
      </div>

      <div class="button-row">
        <button class="secondary-button" type="button" @click="verifyEmail">
          Try Again
        </button>
        <RouterLink class="primary-button" to="/login">Go to Login</RouterLink>
      </div>
    </div>
  </AppPageShell>
</template>
