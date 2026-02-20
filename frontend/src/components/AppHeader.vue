<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Logo / Título -->
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">VOLTIA</span>
          <span class="brand-sub">Sistema de Contadores</span>
        </div>
      </div>

      <!-- Navegación -->
      <nav class="nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ active: isActive(item.to) }"
        >
          <span class="nav-icon" v-html="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span class="nav-indicator" />
        </RouterLink>
      </nav>

      <!-- Estado del sistema -->
      <div class="system-status">
        <span class="status-dot" :class="systemOnline === null ? 'checking' : systemOnline ? 'online' : 'offline'" />
        <span class="status-text">{{ statusLabel }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const systemOnline = ref(null) // null = comprobando
const latencia = ref(null)

const statusLabel = computed(() => {
  if (systemOnline.value === null) return 'Comprobando...'
  if (systemOnline.value) return `Sistema activo${latencia.value ? ` · ${latencia.value}ms` : ''}`
  return 'Sin conexión'
})

const isActive = (path) => route.path.startsWith(path)

const navItems = [
  {
    to: '/dashboard', label: 'Dashboard',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>`
  },
  {
    to: '/clientes', label: 'Clientes',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M19 8v6M22 11h-6"/></svg>`
  },
  {
    to: '/contadores', label: 'Contadores',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/><path d="M7 3.34A9 9 0 0 0 3.34 7"/></svg>`
  },
  {
    to: '/lecturas', label: 'Lecturas',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`
  },
]

// --- Ping a la API cada 30 segundos ---
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
let pingInterval = null

async function pingApi() {
  const t0 = Date.now()
  try {
    const res = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(4000) })
    const data = await res.json()
    systemOnline.value = data.status === 'ok' && data.mongodb === 'ok'
    latencia.value = Date.now() - t0
  } catch {
    systemOnline.value = false
    latencia.value = null
  }
}

onMounted(() => {
  pingApi()
  pingInterval = setInterval(pingApi, 30000)
})

onUnmounted(() => clearInterval(pingInterval))
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #0a0e17;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.4);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.brand-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #00d4ff, #0077ff);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 6px;
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
}

.brand-icon svg {
  width: 100%;
  height: 100%;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.brand-name {
  font-family: 'Share Tech Mono', monospace;
  font-size: 1.1rem;
  color: #e8f4ff;
  letter-spacing: 0.15em;
}

.brand-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.65rem;
  color: #4a6080;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 2px;
}

/* Nav */
.nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  text-decoration: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4a6080;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  color: #a8c8e8;
  background: rgba(255, 255, 255, 0.04);
}

.nav-item.active {
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.08);
}

.nav-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.nav-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.nav-indicator {
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #00d4ff;
  border-radius: 2px 2px 0 0;
  transition: width 0.2s ease;
}

.nav-item.active .nav-indicator {
  width: calc(100% - 1rem);
}

/* Status */
.system-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
  flex-shrink: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #00e676;
  box-shadow: 0 0 8px rgba(0, 230, 118, 0.6);
  animation: pulse 2s infinite;
}

.status-dot.offline {
  background: #ff1744;
  box-shadow: 0 0 8px rgba(255, 23, 68, 0.6);
}

.status-dot.checking {
  background: #ff9100;
  box-shadow: 0 0 8px rgba(255, 145, 0, 0.6);
  animation: pulse 0.8s infinite;
}

.status-text {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.7rem;
  color: #4a6080;
  letter-spacing: 0.05em;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 768px) {
  .brand-sub,
  .nav-label,
  .status-text { display: none; }

  .header-inner { padding: 0 1rem; gap: 1rem; }

  .nav-item { padding: 0.5rem; }

  .nav-icon { width: 20px; height: 20px; }
}
</style>