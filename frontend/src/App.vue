<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Workspace from './Workspace.vue'

type User = { id: number; name: string; email: string }
const user = ref<User | null>(null)
const csrf = ref('')
const mode = ref<'login' | 'register'>('login')
const name = ref('')
const email = ref('')
const password = ref('')
const confirmation = ref('')
const error = ref('')
const busy = ref(false)
const loading = ref(true)

async function request(path: string, body?: object) {
  const response = await fetch(`/api/auth/${path}`, {
    method: body ? 'POST' : 'GET', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'WTaM', 'X-CSRF-Token': csrf.value },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = response.status === 204 ? null : await response.json()
  if (!response.ok) {
    const detail = data?.detail
    throw Object.assign(new Error(typeof detail === 'string' ? detail : detail?.map((item: { msg: string }) => item.msg).join('. ') || 'Request failed.'), { status: response.status })
  }
  return data
}

onMounted(async () => {
  try { const data = await request('me'); user.value = data.user; csrf.value = data.csrf_token }
  catch (e) { if ((e as { status?: number }).status !== 401) error.value = 'Cannot reach the server. Please refresh to try again.' }
  finally { loading.value = false }
})

async function submit() {
  error.value = ''
  if (mode.value === 'register' && password.value !== confirmation.value) { error.value = 'Passwords do not match.'; return }
  busy.value = true
  try {
    const data = await request(mode.value, { name: name.value, email: email.value, password: password.value })
    user.value = data.user; csrf.value = data.csrf_token; password.value = ''; confirmation.value = ''
  } catch (e) { error.value = (e as Error).message }
  finally { busy.value = false }
}

async function logout() {
  busy.value = true; error.value = ''
  try { await request('logout', {}); user.value = null; csrf.value = '' }
  catch (e) { error.value = (e as Error).message }
  finally { busy.value = false }
}
</script>

<template>
  <main :class="{ signed: user }">
    <header v-if="!user" class="site-header"><a class="brand" href="/" aria-label="WTaM home"><span class="brand-mark" aria-hidden="true"></span>wtam.</a></header>
    <section v-if="loading" class="card" aria-live="polite">Loading your workspaceâ€¦</section>
    <section v-else-if="user" class="authenticated"><Workspace :name="user.name" :email="user.email" :busy="busy" @logout="logout" /><p v-if="error" role="alert" class="error">{{ error }}</p></section>
    <section v-else class="card">
      
      <h1>{{ mode === 'login' ? 'Welcome back.' : 'Create account.' }}</h1>
      <form :aria-busy="busy" @submit.prevent="submit">
        <fieldset :disabled="busy">
        <label v-if="mode === 'register'">Name<input v-model="name" autocomplete="name" required maxlength="100" placeholder="Your name"></label>
        <label>Email<input v-model="email" type="email" inputmode="email" autocapitalize="none" :spellcheck="false" autocomplete="username" required maxlength="254" placeholder="you@example.com"></label>
        <label>Password<input v-model="password" type="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" :minlength="mode === 'register' ? 10 : 1" maxlength="128" required placeholder="Your password"></label>
        <template v-if="mode === 'register'"><small>Use at least 10 characters.</small><label>Confirm password<input v-model="confirmation" type="password" autocomplete="new-password" required maxlength="128" placeholder="Repeat your password"></label></template>
        <p v-if="error" role="alert" class="error">{{ error }}</p>
        <button class="primary" :disabled="busy"><span>{{ busy ? 'Please waitâ€¦' : mode === 'login' ? 'Sign in' : 'Create account' }}</span><span aria-hidden="true">â†—</span></button>
        </fieldset>
      </form>
      <p class="switch-mode">{{ mode === 'login' ? 'New here?' : 'Already have an account?' }} <button type="button" :disabled="busy" @click="mode = mode === 'login' ? 'register' : 'login'; error = ''; password = ''; confirmation = ''">{{ mode === 'login' ? 'Create an account' : 'Sign in' }}</button></p>
    </section>
    
  </main>
</template>
