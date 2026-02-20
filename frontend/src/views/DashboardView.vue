<template>
  <div class="dashboard">

    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-sub">Resumen del sistema en tiempo real</p>
      </div>
      <span class="last-update">Actualizado: {{ horaActual }}</span>
    </div>

    <!-- Error global -->
    <div v-if="errorGlobal" class="error-banner">
      ⚠️ {{ errorGlobal }}
      <button @click="errorGlobal = null">✕</button>
    </div>

    <!-- Loading overlay sobre las tarjetas -->
    <div v-if="cargando" class="loading-overlay">
      <div class="spinner" /> Cargando datos del sistema...
    </div>

    <!-- Tarjetas de estadísticas -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <span v-html="stat.icon" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Fila principal -->
    <div class="main-grid">

      <!-- Gráfica de consumo -->
      <div class="card chart-card">
        <div class="card-header">
          <h2 class="card-title">Consumo últimos 7 días</h2>
          <div class="chart-legend">
            <span class="legend-item" v-for="l in chartLegend" :key="l.label">
              <span class="legend-dot" :style="{ background: l.color }" />
              {{ l.label }}
            </span>
          </div>
        </div>
        <div class="chart-area">
          <svg viewBox="0 0 600 200" preserveAspectRatio="none" class="chart-svg">
            <!-- Grid lines -->
            <line v-for="i in 4" :key="i" :x1="0" :y1="i * 40" :x2="600" :y2="i * 40"
              stroke="rgba(255,255,255,0.04)" stroke-width="1" />
            <!-- Líneas de datos -->
            <polyline :points="chartPoints.luz" fill="none" stroke="#00d4ff" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
            <polyline :points="chartPoints.agua" fill="none" stroke="#00e676" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
            <polyline :points="chartPoints.gas" fill="none" stroke="#ff9100" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
            <!-- Área bajo la curva de luz -->
            <polygon :points="chartPoints.luzArea" fill="url(#gradLuz)" opacity="0.15" />
            <defs>
              <linearGradient id="gradLuz" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#00d4ff" />
                <stop offset="100%" stop-color="transparent" />
              </linearGradient>
            </defs>
          </svg>
          <!-- Etiquetas eje X -->
          <div class="chart-labels">
            <span v-for="dia in diasSemana" :key="dia">{{ dia }}</span>
          </div>
        </div>
      </div>

      <!-- Contadores por tipo -->
      <div class="card tipo-card">
        <div class="card-header">
          <h2 class="card-title">Contadores por tipo</h2>
        </div>
        <div class="tipo-list">
          <div class="tipo-item" v-for="tipo in contadoresPorTipo" :key="tipo.label">
            <div class="tipo-info">
              <span class="tipo-icon">{{ tipo.emoji }}</span>
              <span class="tipo-label">{{ tipo.label }}</span>
            </div>
            <div class="tipo-bar-wrap">
              <div class="tipo-bar" :style="{ width: tipo.pct + '%', background: tipo.color }" />
            </div>
            <span class="tipo-count">{{ tipo.count }}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Fila secundaria -->
    <div class="secondary-grid">

      <!-- Alertas -->
      <div class="card alerts-card">
        <div class="card-header">
          <h2 class="card-title">
            Alertas
            <span class="badge-alert">{{ alertas.length }}</span>
          </h2>
        </div>
        <div class="alerts-list">
          <div v-if="alertas.length === 0" class="empty-state">
            Sin alertas activas
          </div>
          <div class="alert-item" v-for="alerta in alertas" :key="alerta.id"
            :class="alerta.tipo.toLowerCase()">
            <div class="alert-dot" />
            <div class="alert-info">
              <span class="alert-serie">{{ alerta.serie }}</span>
              <span class="alert-desc">{{ alerta.desc }}</span>
            </div>
            <span class="alert-tipo">{{ alerta.tipo }}</span>
          </div>
        </div>
      </div>

      <!-- Últimas lecturas -->
      <div class="card lecturas-card">
        <div class="card-header">
          <h2 class="card-title">Últimas lecturas</h2>
        </div>
        <div class="lecturas-list">
          <div class="lectura-item" v-for="lectura in ultimasLecturas" :key="lectura.id">
            <span class="lectura-tipo" :style="{ color: lectura.color }">{{ lectura.emoji }}</span>
            <div class="lectura-info">
              <span class="lectura-serie">{{ lectura.serie }}</span>
              <span class="lectura-fecha">{{ lectura.fecha }}</span>
            </div>
            <span class="lectura-valor">{{ lectura.valor }}</span>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { clientesService, contadoresService, lecturasService } from '@/services/api'

const horaActual = ref(new Date().toLocaleTimeString('es-ES'))

// --- Estado ---
const cargando = ref(true)
const totalClientes = ref('—')
const totalContadoresActivos = ref('—')
const totalLecturasHoy = ref('—')
const totalAlertas = ref('—')
const contadoresPorTipo = ref([])
const alertas = ref([])
const ultimasLecturas = ref([])
const rawData = ref({ luz: [], agua: [], gas: [] })
const errorGlobal = ref(null)

const chartLegend = [
  { label: 'Electricidad', color: '#00d4ff' },
  { label: 'Agua',         color: '#00e676' },
  { label: 'Gas',          color: '#ff9100' },
]
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

// --- Stats cards (reactivas) ---
const stats = computed(() => [
  {
    label: 'Clientes',
    value: totalClientes.value,
    color: 'rgba(0,212,255,0.15)',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M19 8v6M22 11h-6"/></svg>`
  },
  {
    label: 'Contadores activos',
    value: totalContadoresActivos.value,
    color: 'rgba(0,230,118,0.15)',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>`
  },
  {
    label: 'Lecturas hoy',
    value: totalLecturasHoy.value,
    color: 'rgba(255,145,0,0.15)',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#ff9100" stroke-width="1.5" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`
  },
  {
    label: 'Alertas activas',
    value: totalAlertas.value,
    color: 'rgba(255,23,68,0.15)',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#ff1744" stroke-width="1.5" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`
  },
])

// --- Gráfica computed ---
const chartPoints = computed(() => {
  const w = 600, h = 200, pad = 20
  const allVals = [...rawData.value.luz, ...rawData.value.agua, ...rawData.value.gas]
  const max = allVals.length ? Math.max(...allVals) * 1.1 || 1 : 1
  const toX = (i) => pad + (i / 6) * (w - pad * 2)
  const toY = (v) => h - pad - ((v / max) * (h - pad * 2))
  const pts = (arr) => arr.map((v, i) => `${toX(i)},${toY(v)}`).join(' ')
  const luzPts = rawData.value.luz.map((v, i) => `${toX(i)},${toY(v)}`)
  return {
    luz:  pts(rawData.value.luz),
    agua: pts(rawData.value.agua),
    gas:  pts(rawData.value.gas),
    luzArea: rawData.value.luz.length
      ? `${toX(0)},${h} ${luzPts.join(' ')} ${toX(rawData.value.luz.length - 1)},${h}`
      : '',
  }
})

// --- Helpers ---
const emojiTipo = (t) => ({ Electricidad: '⚡', Agua: '💧', Gas: '🔥' }[t] ?? '📊')
const colorTipo = (t) => ({ Electricidad: '#00d4ff', Agua: '#00e676', Gas: '#ff9100' }[t] ?? '#aaa')

function formatValorLectura(l, tipo) {
  if (tipo === 'Electricidad') return `${l.energia_activa_kwh ?? '—'} kWh`
  return `${l.volumen_acumulado_m3 ?? '—'} m³`
}

function tiempoRelativo(fecha) {
  const diff = Math.floor((Date.now() - new Date(fecha)) / 60000)
  if (diff < 1)  return 'ahora mismo'
  if (diff < 60) return `hace ${diff} min`
  const h = Math.floor(diff / 60)
  return `hace ${h}h`
}

// --- Agrupador: consumo diario por tipo (7 días) ---
function consumoDiario(lecturas, tipo) {
  const hoy = new Date()
  return Array.from({ length: 7 }, (_, i) => {
    const dia = new Date(hoy)
    dia.setDate(hoy.getDate() - (6 - i))
    const diaStr = dia.toISOString().slice(0, 10)
    const delDia = lecturas.filter(l =>
      l.tipo === tipo && l.fecha?.slice(0, 10) === diaStr && l.consumo_periodo != null
    )
    return delDia.reduce((acc, l) => acc + (l.consumo_periodo ?? 0), 0)
  })
}

// --- Carga principal ---
onMounted(async () => {
  setInterval(() => { horaActual.value = new Date().toLocaleTimeString('es-ES') }, 1000)

  try {
    // Clientes y contadores en paralelo
    const [clientes, contadores] = await Promise.all([
      clientesService.getAll(0, 1000),
      contadoresService.getAll(0, 1000),
    ])

    totalClientes.value = clientes.length
    totalContadoresActivos.value = contadores.filter(c => c.estado === 'Activo').length

    // Contadores por tipo para las barras
    const tipos = ['Electricidad', 'Agua', 'Gas']
    const colores = { Electricidad: '#00d4ff', Agua: '#00e676', Gas: '#ff9100' }
    const maxTipo = Math.max(...tipos.map(t => contadores.filter(c => c.tipo_suministro === t).length)) || 1
    contadoresPorTipo.value = tipos.map(t => {
      const count = contadores.filter(c => c.tipo_suministro === t).length
      return { label: t, emoji: emojiTipo(t), count, pct: Math.round((count / maxTipo) * 100), color: colores[t] }
    })

    // Alertas: contadores averiados o saboteados
    const conProblemas = contadores.filter(c => c.estado !== 'Activo')
    totalAlertas.value = conProblemas.length
    alertas.value = conProblemas.slice(0, 5).map(c => ({
      id: c._id, serie: c.numero_serie,
      desc: c.estado === 'Saboteado' ? 'Contador saboteado detectado' : 'Contador averiado',
      tipo: c.estado,
    }))

    // Lecturas: traer las últimas 20 de cada contador
    const hoy = new Date().toISOString().slice(0, 10)
    const todasLecturas = []
    await Promise.all(contadores.map(async c => {
      try {
        const ls = await lecturasService.getByContador(c._id, 0, 20)
        ls.forEach(l => todasLecturas.push({
          ...l.datos,
          _id: l._id,
          contador_id: l.contador_id,
          consumo_periodo: l.consumo_periodo,
          tipo: c.tipo_suministro,
          numero_serie: c.numero_serie,
        }))
      } catch {}
    }))

    // Lecturas de hoy
    totalLecturasHoy.value = todasLecturas.filter(l => l.fecha?.slice(0, 10) === hoy).length

    // Gráfica: consumo diario por tipo últimos 7 días
    rawData.value = {
      luz:  consumoDiario(todasLecturas, 'Electricidad'),
      agua: consumoDiario(todasLecturas, 'Agua'),
      gas:  consumoDiario(todasLecturas, 'Gas'),
    }

    // Últimas 5 lecturas ordenadas por fecha
    ultimasLecturas.value = [...todasLecturas]
      .sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
      .slice(0, 5)
      .map(l => ({
        id: l._id, serie: l.numero_serie,
        emoji: emojiTipo(l.tipo), color: colorTipo(l.tipo),
        valor: formatValorLectura(l, l.tipo),
        fecha: tiempoRelativo(l.fecha),
      }))

  } catch (e) {
    errorGlobal.value = e.message
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.dashboard {
  min-height: 100vh;
  background: #080c14;
  padding: 2rem;
  font-family: 'DM Sans', sans-serif;
  color: #e8f4ff;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 600;
  color: #e8f4ff;
  margin: 0;
}

.page-sub {
  font-size: 0.8rem;
  color: #4a6080;
  margin: 0.2rem 0 0;
}

.last-update {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.7rem;
  color: #4a6080;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: #0e1420;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 10px;
}

.stat-icon :deep(svg) { width: 24px; height: 24px; }

.stat-info { display: flex; flex-direction: column; }

.stat-value {
  font-family: 'Share Tech Mono', monospace;
  font-size: 1.5rem;
  color: #e8f4ff;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #4a6080;
  margin-top: 4px;
}

/* Grids */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1rem;
  margin-bottom: 1rem;
}

.secondary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Card base */
.card {
  background: #0e1420;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.card-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #a8c8e8;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Chart */
.chart-legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: #4a6080;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chart-area { position: relative; }

.chart-svg {
  width: 100%;
  height: 160px;
  display: block;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0.5rem 0;
}

.chart-labels span {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.65rem;
  color: #4a6080;
}

/* Tipo */
.tipo-list { display: flex; flex-direction: column; gap: 1rem; }

.tipo-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tipo-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 110px;
  flex-shrink: 0;
}

.tipo-icon { font-size: 1rem; }

.tipo-label {
  font-size: 0.8rem;
  color: #a8c8e8;
}

.tipo-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
}

.tipo-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.tipo-count {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.8rem;
  color: #4a6080;
  width: 30px;
  text-align: right;
}

/* Alertas */
.badge-alert {
  background: rgba(255,23,68,0.2);
  color: #ff1744;
  font-size: 0.65rem;
  padding: 2px 7px;
  border-radius: 99px;
  font-family: 'Share Tech Mono', monospace;
}

.alerts-list { display: flex; flex-direction: column; gap: 0.6rem; }

.alert-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
}

.alert-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.alert-item.averiado .alert-dot { background: #ff9100; box-shadow: 0 0 6px rgba(255,145,0,0.5); }
.alert-item.saboteado .alert-dot { background: #ff1744; box-shadow: 0 0 6px rgba(255,23,68,0.5); }

.alert-info { flex: 1; display: flex; flex-direction: column; }

.alert-serie {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  color: #e8f4ff;
}

.alert-desc {
  font-size: 0.7rem;
  color: #4a6080;
  margin-top: 2px;
}

.alert-tipo {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 99px;
}

.alert-item.averiado .alert-tipo { background: rgba(255,145,0,0.15); color: #ff9100; }
.alert-item.saboteado .alert-tipo { background: rgba(255,23,68,0.15); color: #ff1744; }

/* Lecturas */
.lecturas-list { display: flex; flex-direction: column; gap: 0.6rem; }

.lectura-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
}

.lectura-tipo { font-size: 1.1rem; }

.lectura-info { flex: 1; display: flex; flex-direction: column; }

.lectura-serie {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  color: #e8f4ff;
}

.lectura-fecha {
  font-size: 0.7rem;
  color: #4a6080;
  margin-top: 2px;
}

.lectura-valor {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.8rem;
  color: #a8c8e8;
}

.empty-state {
  text-align: center;
  color: #4a6080;
  font-size: 0.8rem;
  padding: 1rem;
}

@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .main-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .dashboard { padding: 1rem; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .secondary-grid { grid-template-columns: 1fr; }
}

/* Error / Loading */
.error-banner {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(255,23,68,0.1); border: 1px solid rgba(255,23,68,0.3);
  color: #ff1744; padding: 0.75rem 1rem; border-radius: 8px;
  font-size: 0.85rem; margin-bottom: 1rem;
}
.error-banner button { background: none; border: none; color: #ff1744; cursor: pointer; font-size: 1rem; }

.loading-overlay {
  display: flex; align-items: center; justify-content: center; gap: 0.75rem;
  background: rgba(8,12,20,0.7); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px; padding: 2rem; color: #4a6080; font-size: 0.85rem;
  margin-bottom: 1.5rem;
}
.spinner {
  width: 20px; height: 20px;
  border: 2px solid rgba(0,212,255,0.2); border-top-color: #00d4ff;
  border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>