<template>
  <div class="lecturas">

    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Lecturas</h1>
        <p class="page-sub">{{ lecturasFiltradas.length }} lecturas encontradas</p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <div class="filtro-chips">
        <button
          v-for="tipo in tiposFiltro" :key="tipo.value"
          class="chip" :class="{ active: filtroTipo === tipo.value }"
          @click="filtroTipo = filtroTipo === tipo.value ? null : tipo.value"
        >
          {{ tipo.emoji }} {{ tipo.label }}
        </button>
      </div>
      <div class="filtro-fechas">
        <div class="fecha-group">
          <label>Desde</label>
          <input type="date" v-model="fechaDesde" class="input-fecha" />
        </div>
        <div class="fecha-group">
          <label>Hasta</label>
          <input type="date" v-model="fechaHasta" class="input-fecha" />
        </div>
        <button v-if="fechaDesde || fechaHasta" class="btn-clear" @click="limpiarFechas">✕ Limpiar</button>
      </div>
    </div>

    <!-- Tabla -->
    <div class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Nº Serie</th>
            <th>Fecha</th>
            <th>Valor acumulado</th>
            <th>Consumo periodo</th>
            <th>Detalle</th>
            <th>Gráfica</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="lecturasFiltradas.length === 0">
            <td colspan="7" class="empty-row">No se encontraron lecturas</td>
          </tr>
          <tr v-for="lectura in lecturasFiltradas" :key="lectura.id" class="tabla-row">
            <td>
              <span class="tipo-badge" :class="lectura.tipo.toLowerCase()">
                {{ emojiTipo(lectura.tipo) }} {{ lectura.tipo }}
              </span>
            </td>
            <td class="mono">{{ lectura.numero_serie }}</td>
            <td class="mono text-muted">{{ formatFecha(lectura.fecha) }}</td>
            <td class="mono">
              {{ valorAcumulado(lectura) }}
            </td>
            <td>
              <span v-if="lectura.consumo_periodo !== null" class="consumo"
                :class="{ alto: lectura.consumo_periodo > umbralAlto(lectura.tipo) }">
                {{ lectura.consumo_periodo }} {{ unidad(lectura.tipo) }}
              </span>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <button class="btn-icon view" @click="abrirDetalle(lectura)" title="Ver detalle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </td>
            <td>
              <button class="btn-icon chart" @click="abrirGrafica(lectura)" title="Ver gráfica">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL: Detalle lectura -->
    <Transition name="modal">
      <div v-if="modalDetalle" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">
              {{ emojiTipo(lecturaSeleccionada?.tipo) }} Detalle — {{ lecturaSeleccionada?.numero_serie }}
            </h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body" v-if="lecturaSeleccionada">

            <!-- Electricidad -->
            <div v-if="lecturaSeleccionada.tipo === 'Electricidad'" class="campos-grid">
              <div class="campo"><span class="campo-label">Energía activa</span><span class="campo-valor azul">{{ lecturaSeleccionada.datos.energia_activa_kwh }} kWh</span></div>
              <div class="campo"><span class="campo-label">Energía reactiva</span><span class="campo-valor">{{ lecturaSeleccionada.datos.energia_reactiva_kvarh }} kVArh</span></div>
              <div class="campo"><span class="campo-label">Potencia activa</span><span class="campo-valor">{{ lecturaSeleccionada.datos.potencia_activa_kw }} kW</span></div>
              <div class="campo"><span class="campo-label">Potencia reactiva</span><span class="campo-valor">{{ lecturaSeleccionada.datos.potencia_reactiva_kvar }} kVAr</span></div>
              <div class="campo"><span class="campo-label">Voltaje</span><span class="campo-valor">{{ lecturaSeleccionada.datos.voltaje_v }} V</span></div>
              <div class="campo"><span class="campo-label">Corriente</span><span class="campo-valor">{{ lecturaSeleccionada.datos.corriente_a }} A</span></div>
              <div class="campo"><span class="campo-label">Factor de potencia</span><span class="campo-valor">{{ lecturaSeleccionada.datos.factor_potencia }}</span></div>
              <div class="campo"><span class="campo-label">Frecuencia</span><span class="campo-valor">{{ lecturaSeleccionada.datos.frecuencia_hz }} Hz</span></div>
            </div>

            <!-- Agua -->
            <div v-if="lecturaSeleccionada.tipo === 'Agua'" class="campos-grid">
              <div class="campo"><span class="campo-label">Volumen acumulado</span><span class="campo-valor verde">{{ lecturaSeleccionada.datos.volumen_acumulado_m3 }} m³</span></div>
              <div class="campo"><span class="campo-label">Caudal</span><span class="campo-valor">{{ lecturaSeleccionada.datos.caudal_m3h }} m³/h</span></div>
              <div class="campo"><span class="campo-label">Presión</span><span class="campo-valor">{{ lecturaSeleccionada.datos.presion_bar }} bar</span></div>
              <div class="campo"><span class="campo-label">Temperatura</span><span class="campo-valor">{{ lecturaSeleccionada.datos.temperatura_c }} °C</span></div>
            </div>

            <!-- Gas -->
            <div v-if="lecturaSeleccionada.tipo === 'Gas'" class="campos-grid">
              <div class="campo"><span class="campo-label">Volumen acumulado</span><span class="campo-valor naranja">{{ lecturaSeleccionada.datos.volumen_acumulado_m3 }} m³</span></div>
              <div class="campo"><span class="campo-label">Caudal</span><span class="campo-valor">{{ lecturaSeleccionada.datos.caudal_m3h }} m³/h</span></div>
              <div class="campo"><span class="campo-label">Presión</span><span class="campo-valor">{{ lecturaSeleccionada.datos.presion_mbar }} mbar</span></div>
              <div class="campo"><span class="campo-label">Temperatura</span><span class="campo-valor">{{ lecturaSeleccionada.datos.temperatura_c }} °C</span></div>
              <div class="campo full"><span class="campo-label">Poder calorífico</span><span class="campo-valor">{{ lecturaSeleccionada.datos.poder_calorifico_kwh_m3 }} kWh/m³</span></div>
            </div>

            <div class="campo-fecha">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:14px;height:14px">
                <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>
              </svg>
              {{ formatFechaCompleta(lecturaSeleccionada.fecha) }}
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cerrar</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Gráfica de consumo -->
    <Transition name="modal">
      <div v-if="modalGrafica" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h2 class="modal-title">
              Consumo — {{ lecturaSeleccionada?.numero_serie }}
            </h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body" v-if="lecturaSeleccionada">
            <div class="chart-container">
              <svg viewBox="0 0 600 220" preserveAspectRatio="none" class="chart-svg">
                <!-- Grid -->
                <line v-for="i in 4" :key="i" :x1="40" :y1="i * 40" :x2="580" :y2="i * 40"
                  stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
                <!-- Barras -->
                <rect v-for="(bar, i) in graficaData" :key="i"
                  :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h"
                  :fill="colorTipo(lecturaSeleccionada.tipo)" opacity="0.7" rx="3"/>
                <!-- Etiquetas Y -->
                <text v-for="i in 4" :key="'y'+i" :x="35" :y="i * 40 + 4"
                  fill="#4a6080" font-size="10" text-anchor="end">{{ Math.round(maxGrafica - (i-1) * (maxGrafica/4)) }}</text>
              </svg>
              <div class="chart-labels">
                <span v-for="(bar, i) in graficaData" :key="i">{{ bar.label }}</span>
              </div>
            </div>
            <div class="grafica-stats">
              <div class="gstat"><span class="gstat-label">Máximo</span><span class="gstat-valor">{{ maxConsumo }} {{ unidad(lecturaSeleccionada.tipo) }}</span></div>
              <div class="gstat"><span class="gstat-label">Mínimo</span><span class="gstat-valor">{{ minConsumo }} {{ unidad(lecturaSeleccionada.tipo) }}</span></div>
              <div class="gstat"><span class="gstat-label">Media</span><span class="gstat-valor">{{ mediaConsumo }} {{ unidad(lecturaSeleccionada.tipo) }}</span></div>
              <div class="gstat"><span class="gstat-label">Total</span><span class="gstat-valor">{{ totalConsumo }} {{ unidad(lecturaSeleccionada.tipo) }}</span></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cerrar</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// --- Estado ---
const filtroTipo = ref(null)
const fechaDesde = ref('')
const fechaHasta = ref('')
const modalDetalle = ref(false)
const modalGrafica = ref(false)
const lecturaSeleccionada = ref(null)

const tiposFiltro = [
  { value: 'Electricidad', label: 'Electricidad', emoji: '⚡' },
  { value: 'Agua',         label: 'Agua',         emoji: '💧' },
  { value: 'Gas',          label: 'Gas',          emoji: '🔥' },
]

// Datos de ejemplo — se reemplazarán con la API
const lecturas = ref([
  {
    id: '1', numero_serie: 'SN-2024-001', tipo: 'Electricidad',
    fecha: '2025-02-19T10:00:00', consumo_periodo: 145.2,
    datos: { energia_activa_kwh: 1523.4, energia_reactiva_kvarh: 210.1, potencia_activa_kw: 2.51,
      potencia_reactiva_kvar: 0.8, voltaje_v: 230.1, corriente_a: 10.9, factor_potencia: 0.95, frecuencia_hz: 50.01 }
  },
  {
    id: '2', numero_serie: 'SN-2024-002', tipo: 'Agua',
    fecha: '2025-02-19T10:05:00', consumo_periodo: 8.3,
    datos: { volumen_acumulado_m3: 108.4, caudal_m3h: 0.4, presion_bar: 3.1, temperatura_c: 14.2 }
  },
  {
    id: '3', numero_serie: 'SN-2024-003', tipo: 'Gas',
    fecha: '2025-02-19T10:10:00', consumo_periodo: 62.1,
    datos: { volumen_acumulado_m3: 560.3, caudal_m3h: 1.2, presion_mbar: 21.5, temperatura_c: 8.4, poder_calorifico_kwh_m3: 11.2 }
  },
  {
    id: '4', numero_serie: 'SN-2024-001', tipo: 'Electricidad',
    fecha: '2025-02-18T10:00:00', consumo_periodo: 138.7,
    datos: { energia_activa_kwh: 1378.2, energia_reactiva_kvarh: 198.4, potencia_activa_kw: 1.8,
      potencia_reactiva_kvar: 0.6, voltaje_v: 229.8, corriente_a: 7.8, factor_potencia: 0.94, frecuencia_hz: 49.99 }
  },
  {
    id: '5', numero_serie: 'SN-2024-002', tipo: 'Agua',
    fecha: '2025-02-18T10:05:00', consumo_periodo: 7.1,
    datos: { volumen_acumulado_m3: 100.1, caudal_m3h: 0.3, presion_bar: 3.0, temperatura_c: 13.8 }
  },
])

// Datos simulados de consumo para la gráfica (últimos 7 días)
const consumoHistorico = {
  'SN-2024-001': [138, 145, 132, 160, 138, 95, 110],
  'SN-2024-002': [7.1, 8.3, 6.9, 9.1, 8.8, 5.2, 6.7],
  'SN-2024-003': [58, 62, 55, 70, 65, 42, 48],
}
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

// --- Computed ---
const lecturasFiltradas = computed(() => {
  return lecturas.value.filter(l => {
    const matchTipo = !filtroTipo.value || l.tipo === filtroTipo.value
    const fecha = new Date(l.fecha)
    const matchDesde = !fechaDesde.value || fecha >= new Date(fechaDesde.value)
    const matchHasta = !fechaHasta.value || fecha <= new Date(fechaHasta.value + 'T23:59:59')
    return matchTipo && matchDesde && matchHasta
  })
})

const graficaData = computed(() => {
  if (!lecturaSeleccionada.value) return []
  const data = consumoHistorico[lecturaSeleccionada.value.numero_serie] ?? [0,0,0,0,0,0,0]
  const max = Math.max(...data)
  const w = 60, gap = 20, padL = 50, h = 160, padTop = 20
  return data.map((v, i) => ({
    x: padL + i * (w + gap),
    y: padTop + h - (v / max) * h,
    w, h: (v / max) * h,
    label: diasSemana[i],
  }))
})

const maxGrafica = computed(() => {
  if (!lecturaSeleccionada.value) return 0
  const data = consumoHistorico[lecturaSeleccionada.value.numero_serie] ?? []
  return Math.max(...data)
})

const consumosArray = computed(() => {
  if (!lecturaSeleccionada.value) return []
  return consumoHistorico[lecturaSeleccionada.value.numero_serie] ?? []
})

const maxConsumo = computed(() => Math.max(...consumosArray.value).toFixed(1))
const minConsumo = computed(() => Math.min(...consumosArray.value).toFixed(1))
const mediaConsumo = computed(() => (consumosArray.value.reduce((a, b) => a + b, 0) / consumosArray.value.length).toFixed(1))
const totalConsumo = computed(() => consumosArray.value.reduce((a, b) => a + b, 0).toFixed(1))

// --- Helpers ---
const emojiTipo = (t) => ({ Electricidad: '⚡', Agua: '💧', Gas: '🔥' }[t] ?? '📊')
const colorTipo = (t) => ({ Electricidad: '#00d4ff', Agua: '#00e676', Gas: '#ff9100' }[t] ?? '#fff')
const unidad = (t) => ({ Electricidad: 'kWh', Agua: 'm³', Gas: 'm³' }[t] ?? '')
const umbralAlto = (t) => ({ Electricidad: 150, Agua: 10, Gas: 80 }[t] ?? 999)

const valorAcumulado = (l) => {
  if (l.tipo === 'Electricidad') return `${l.datos.energia_activa_kwh} kWh`
  return `${l.datos.volumen_acumulado_m3} m³`
}

const formatFecha = (f) => new Date(f).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
const formatFechaCompleta = (f) => new Date(f).toLocaleString('es-ES', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })

// --- Modales ---
const abrirDetalle = (lectura) => { lecturaSeleccionada.value = lectura; modalDetalle.value = true }
const abrirGrafica = (lectura) => { lecturaSeleccionada.value = lectura; modalGrafica.value = true }
const cerrarModal = () => { modalDetalle.value = false; modalGrafica.value = false; lecturaSeleccionada.value = null }
const limpiarFechas = () => { fechaDesde.value = ''; fechaHasta.value = '' }
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.lecturas {
  min-height: 100vh;
  background: #080c14;
  padding: 2rem;
  font-family: 'DM Sans', sans-serif;
  color: #e8f4ff;
}

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 1.6rem; font-weight: 600; margin: 0; }
.page-sub { font-size: 0.8rem; color: #4a6080; margin: 0.2rem 0 0; }

/* Filtros */
.filtros { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; margin-bottom: 1.5rem; }
.filtro-chips { display: flex; gap: 0.4rem; }
.chip {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  color: #4a6080; padding: 0.35rem 0.85rem; border-radius: 99px;
  font-size: 0.78rem; cursor: pointer; transition: all 0.2s; font-family: 'DM Sans', sans-serif;
}
.chip:hover { background: rgba(255,255,255,0.08); color: #a8c8e8; }
.chip.active { background: rgba(0,212,255,0.12); border-color: rgba(0,212,255,0.3); color: #00d4ff; }

.filtro-fechas { display: flex; align-items: center; gap: 0.75rem; margin-left: auto; }
.fecha-group { display: flex; align-items: center; gap: 0.4rem; }
.fecha-group label { font-size: 0.72rem; color: #4a6080; text-transform: uppercase; letter-spacing: 0.06em; }
.input-fecha {
  background: #0e1420; border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; padding: 0.45rem 0.75rem; color: #e8f4ff;
  font-family: 'DM Sans', sans-serif; font-size: 0.8rem; outline: none;
  color-scheme: dark;
}
.input-fecha:focus { border-color: #00d4ff; }
.btn-clear {
  background: none; border: none; color: #4a6080; font-size: 0.75rem;
  cursor: pointer; transition: color 0.2s; font-family: 'DM Sans', sans-serif;
}
.btn-clear:hover { color: #ff1744; }

/* Tabla */
.table-wrap { background: #0e1420; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; overflow: auto; }
.tabla { width: 100%; border-collapse: collapse; min-width: 800px; }
.tabla thead tr { background: rgba(255,255,255,0.03); border-bottom: 1px solid rgba(255,255,255,0.06); }
.tabla th { text-align: left; padding: 0.9rem 1rem; font-size: 0.72rem; font-weight: 600; color: #4a6080; text-transform: uppercase; letter-spacing: 0.08em; }
.tabla-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.tabla-row:last-child { border-bottom: none; }
.tabla-row:hover { background: rgba(255,255,255,0.02); }
.tabla td { padding: 0.85rem 1rem; font-size: 0.85rem; }

.tipo-badge { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 500; }
.tipo-badge.electricidad { background: rgba(0,212,255,0.12); color: #00d4ff; border: 1px solid rgba(0,212,255,0.2); }
.tipo-badge.agua { background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.2); }
.tipo-badge.gas { background: rgba(255,145,0,0.12); color: #ff9100; border: 1px solid rgba(255,145,0,0.2); }

.mono { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.text-muted { color: #4a6080; }
.consumo { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #a8c8e8; }
.consumo.alto { color: #ff9100; }
.empty-row { text-align: center; color: #4a6080; padding: 2rem; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.btn-icon svg { width: 15px; height: 15px; }
.btn-icon.view { background: rgba(0,212,255,0.08); color: #00d4ff; }
.btn-icon.view:hover { background: rgba(0,212,255,0.18); }
.btn-icon.chart { background: rgba(0,230,118,0.08); color: #00e676; }
.btn-icon.chart:hover { background: rgba(0,230,118,0.18); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem; }
.modal { background: #0e1420; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; width: 100%; max-width: 520px; box-shadow: 0 24px 64px rgba(0,0,0,0.6); }
.modal-lg { max-width: 700px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.modal-title { font-size: 1rem; font-weight: 600; margin: 0; }
.btn-close { background: none; border: none; color: #4a6080; font-size: 1rem; cursor: pointer; padding: 0.25rem; transition: color 0.2s; }
.btn-close:hover { color: #e8f4ff; }
.modal-body { padding: 1.5rem; }
.modal-footer { display: flex; justify-content: flex-end; padding: 1.25rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.06); }
.btn-secondary { background: rgba(255,255,255,0.06); color: #a8c8e8; border: 1px solid rgba(255,255,255,0.1); padding: 0.6rem 1.2rem; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 0.85rem; cursor: pointer; }

/* Detalle campos */
.campos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem; }
.campo { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.3rem; }
.campo.full { grid-column: 1 / -1; }
.campo-label { font-size: 0.7rem; color: #4a6080; text-transform: uppercase; letter-spacing: 0.06em; }
.campo-valor { font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; color: #e8f4ff; }
.campo-valor.azul { color: #00d4ff; }
.campo-valor.verde { color: #00e676; }
.campo-valor.naranja { color: #ff9100; }
.campo-fecha { display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; color: #4a6080; margin-top: 0.5rem; font-family: 'Share Tech Mono', monospace; }

/* Gráfica */
.chart-container { position: relative; margin-bottom: 1.5rem; }
.chart-svg { width: 100%; height: 200px; display: block; }
.chart-labels { display: flex; justify-content: space-around; padding: 0.4rem 3rem 0; }
.chart-labels span { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #4a6080; }

.grafica-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }
.gstat { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.3rem; text-align: center; }
.gstat-label { font-size: 0.7rem; color: #4a6080; text-transform: uppercase; letter-spacing: 0.06em; }
.gstat-valor { font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: #e8f4ff; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95) translateY(10px); }
</style>