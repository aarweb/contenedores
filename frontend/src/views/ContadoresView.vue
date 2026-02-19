<template>
  <div class="contadores">

    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Contadores</h1>
        <p class="page-sub">{{ contadoresFiltrados.length }} contadores encontrados</p>
      </div>
      <button class="btn-primary" @click="abrirModalCrear">
        <span>+</span> Nuevo contador
      </button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <div class="search-bar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input v-model="busqueda" type="text" placeholder="Buscar por serie o CUPS..." class="search-input" />
      </div>
      <div class="filtro-chips">
        <button
          v-for="tipo in tiposFiltro" :key="tipo.value"
          class="chip" :class="{ active: filtroTipo === tipo.value }"
          @click="filtroTipo = filtroTipo === tipo.value ? null : tipo.value"
        >
          {{ tipo.emoji }} {{ tipo.label }}
        </button>
      </div>
      <div class="filtro-chips">
        <button
          v-for="estado in estadosFiltro" :key="estado.value"
          class="chip estado" :class="[{ active: filtroEstado === estado.value }, estado.value.toLowerCase()]"
          @click="filtroEstado = filtroEstado === estado.value ? null : estado.value"
        >
          {{ estado.label }}
        </button>
      </div>
    </div>

    <!-- Tabla -->
    <div class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Nº Serie</th>
            <th>CUPS / Póliza</th>
            <th>Marca / Modelo</th>
            <th>Dirección</th>
            <th>Estado</th>
            <th>Clientes</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="contadoresFiltrados.length === 0">
            <td colspan="8" class="empty-row">No se encontraron contadores</td>
          </tr>
          <tr v-for="contador in contadoresFiltrados" :key="contador.id" class="tabla-row">
            <td>
              <span class="tipo-badge" :class="contador.tipo_suministro.toLowerCase()">
                {{ emojiTipo(contador.tipo_suministro) }} {{ contador.tipo_suministro }}
              </span>
            </td>
            <td class="mono">{{ contador.numero_serie }}</td>
            <td class="mono text-muted">{{ contador.cups_poliza }}</td>
            <td>
              <span class="marca">{{ contador.marca }}</span>
              <span class="modelo">{{ contador.modelo }}</span>
            </td>
            <td class="dir">
              {{ contador.direccion_fisica }}
              <button class="btn-mapa" @click="abrirMapa(contador)" title="Ver en mapa">🗺️</button>
            </td>
            <td>
              <span class="estado-badge" :class="contador.estado.toLowerCase()">
                {{ contador.estado }}
              </span>
            </td>
            <td>
              <button class="btn-clientes" @click="abrirClientes(contador)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <circle cx="8" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
                </svg>
                {{ contador.clientes?.length ?? 0 }}
              </button>
            </td>
            <td>
              <div class="acciones">
                <button class="btn-icon edit" @click="abrirModalEditar(contador)" title="Editar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="btn-icon delete" @click="confirmarEliminar(contador)" title="Eliminar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                    <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
                    <path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL: Crear / Editar -->
    <Transition name="modal">
      <div v-if="modalFormulario" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h2 class="modal-title">{{ modoEdicion ? 'Editar contador' : 'Nuevo contador' }}</h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid">

              <div class="form-group">
                <label>Nº de serie</label>
                <input v-model="form.numero_serie" :disabled="modoEdicion" type="text" placeholder="SN-2026-001" :class="{ error: errores.numero_serie }" />
                <span v-if="errores.numero_serie" class="error-msg">{{ errores.numero_serie }}</span>
              </div>

              <div class="form-group">
                <label>CUPS / Póliza</label>
                <input v-model="form.cups_poliza" type="text" placeholder="ES0021000000000000XX" :class="{ error: errores.cups_poliza }" />
                <span v-if="errores.cups_poliza" class="error-msg">{{ errores.cups_poliza }}</span>
              </div>

              <div class="form-group">
                <label>Tipo de suministro</label>
                <select v-model="form.tipo_suministro" :class="{ error: errores.tipo_suministro }">
                  <option value="">Seleccionar...</option>
                  <option value="Electricidad">⚡ Electricidad</option>
                  <option value="Agua">💧 Agua</option>
                  <option value="Gas">🔥 Gas</option>
                </select>
                <span v-if="errores.tipo_suministro" class="error-msg">{{ errores.tipo_suministro }}</span>
              </div>

              <div class="form-group">
                <label>Estado</label>
                <select v-model="form.estado">
                  <option value="Activo">Activo</option>
                  <option value="Averiado">Averiado</option>
                  <option value="Saboteado">Saboteado</option>
                </select>
              </div>

              <div class="form-group">
                <label>Marca</label>
                <input v-model="form.marca" type="text" placeholder="Siemens" :class="{ error: errores.marca }" />
                <span v-if="errores.marca" class="error-msg">{{ errores.marca }}</span>
              </div>

              <div class="form-group">
                <label>Modelo</label>
                <input v-model="form.modelo" type="text" placeholder="SmartMeter-V3" :class="{ error: errores.modelo }" />
                <span v-if="errores.modelo" class="error-msg">{{ errores.modelo }}</span>
              </div>

              <div class="form-group">
                <label>Versión firmware</label>
                <input v-model="form.version_firmware" type="text" placeholder="v1.2.4" :class="{ error: errores.version_firmware }" />
                <span v-if="errores.version_firmware" class="error-msg">{{ errores.version_firmware }}</span>
              </div>

              <div class="form-group full">
                <label>Dirección física</label>
                <input v-model="form.direccion_fisica" type="text" placeholder="Calle Mayor 1, Madrid" :class="{ error: errores.direccion_fisica }" />
                <span v-if="errores.direccion_fisica" class="error-msg">{{ errores.direccion_fisica }}</span>
              </div>

              <div class="form-group">
                <label>Latitud</label>
                <input v-model.number="form.latitud" type="number" placeholder="40.4167" step="0.0001" :class="{ error: errores.latitud }" />
                <span v-if="errores.latitud" class="error-msg">{{ errores.latitud }}</span>
              </div>

              <div class="form-group">
                <label>Longitud</label>
                <input v-model.number="form.longitud" type="number" placeholder="-3.7033" step="0.0001" :class="{ error: errores.longitud }" />
                <span v-if="errores.longitud" class="error-msg">{{ errores.longitud }}</span>
              </div>

            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button class="btn-primary" @click="guardarContador">
              {{ modoEdicion ? 'Guardar cambios' : 'Crear contador' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Clientes asignados -->
    <Transition name="modal">
      <div v-if="modalClientes" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">
              Clientes de {{ contadorSeleccionado?.numero_serie }}
            </h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <div v-if="!contadorSeleccionado?.clientes?.length" class="empty-state">
              Este contador no tiene clientes asignados
            </div>
            <div v-else class="clientes-list">
              <div class="cliente-item" v-for="c in contadorSeleccionado.clientes" :key="c.id">
                <div class="avatar">{{ `${c.nombre[0]}${c.apellidos[0]}`.toUpperCase() }}</div>
                <div class="cliente-info">
                  <span class="cliente-nombre">{{ c.nombre }} {{ c.apellidos }}</span>
                  <span class="cliente-email">{{ c.email }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cerrar</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Mapa -->
    <Transition name="modal">
      <div v-if="modalMapa" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h2 class="modal-title">
              {{ contadorSeleccionado?.numero_serie }} — {{ contadorSeleccionado?.direccion_fisica }}
            </h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body" style="padding: 0">
            <div id="mapa" style="height: 400px; width: 100%; border-radius: 0 0 16px 16px;" />
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Confirmar eliminar -->
    <Transition name="modal">
      <div v-if="modalEliminar" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2 class="modal-title">Eliminar contador</h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <p class="confirm-text">
              ¿Estás seguro de que quieres eliminar el contador
              <strong>{{ contadorAEliminar?.numero_serie }}</strong>?
              Esta acción no se puede deshacer.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button class="btn-danger" @click="eliminarContador">Eliminar</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
L.Marker.prototype.options.icon = L.icon({
  iconUrl, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41]
})

// --- Estado ---
const busqueda = ref('')
const filtroTipo = ref(null)
const filtroEstado = ref(null)
const modalFormulario = ref(false)
const modalClientes = ref(false)
const modalEliminar = ref(false)
const modalMapa = ref(false)
let mapaInstancia = null
const modoEdicion = ref(false)
const contadorSeleccionado = ref(null)
const contadorAEliminar = ref(null)
const errores = ref({})

const formVacio = {
  numero_serie: '', cups_poliza: '', marca: '', modelo: '',
  version_firmware: '', direccion_fisica: '', tipo_suministro: '',
  estado: 'Activo', latitud: null, longitud: null
}
const form = ref({ ...formVacio })

const tiposFiltro = [
  { value: 'Electricidad', label: 'Electricidad', emoji: '⚡' },
  { value: 'Agua',         label: 'Agua',         emoji: '💧' },
  { value: 'Gas',          label: 'Gas',          emoji: '🔥' },
]

const estadosFiltro = [
  { value: 'Activo',    label: 'Activo'    },
  { value: 'Averiado',  label: 'Averiado'  },
  { value: 'Saboteado', label: 'Saboteado' },
]

// Datos de ejemplo — se reemplazarán con la API
const contadores = ref([
  {
    id: '1', numero_serie: 'SN-2024-001', cups_poliza: 'ES0021000000000001XX',
    marca: 'Siemens', modelo: 'SmartMeter-V3', version_firmware: 'v1.2.4',
    direccion_fisica: 'Calle Mayor 1, Madrid', tipo_suministro: 'Electricidad',
    estado: 'Activo', latitud: 40.4167, longitud: -3.7033,
    clientes: [{ id: '1', nombre: 'Juan', apellidos: 'García', email: 'juan@email.com' }]
  },
  {
    id: '2', numero_serie: 'SN-2024-002', cups_poliza: 'ES0021000000000002XX',
    marca: 'Itron', modelo: 'Aquadis+', version_firmware: 'v2.0.1',
    direccion_fisica: 'Av. Libertad 24, Valencia', tipo_suministro: 'Agua',
    estado: 'Activo', latitud: 39.4699, longitud: -0.3763,
    clientes: []
  },
  {
    id: '3', numero_serie: 'SN-2024-003', cups_poliza: 'ES0021000000000003XX',
    marca: 'Honeywell', modelo: 'EK280', version_firmware: 'v3.1.0',
    direccion_fisica: 'Plaza España 3, Sevilla', tipo_suministro: 'Gas',
    estado: 'Averiado', latitud: 37.3891, longitud: -5.9845,
    clientes: [
      { id: '2', nombre: 'María', apellidos: 'Martínez', email: 'maria@email.com' },
      { id: '3', nombre: 'Carlos', apellidos: 'Fernández', email: 'carlos@email.com' }
    ]
  },
])

// --- Computed ---
const contadoresFiltrados = computed(() => {
  return contadores.value.filter(c => {
    const q = busqueda.value.toLowerCase()
    const matchBusqueda = !q || c.numero_serie.toLowerCase().includes(q) || c.cups_poliza.toLowerCase().includes(q)
    const matchTipo = !filtroTipo.value || c.tipo_suministro === filtroTipo.value
    const matchEstado = !filtroEstado.value || c.estado === filtroEstado.value
    return matchBusqueda && matchTipo && matchEstado
  })
})

// --- Helpers ---
const emojiTipo = (t) => ({ Electricidad: '⚡', Agua: '💧', Gas: '🔥' }[t] ?? '📊')

// --- Modales ---
const abrirModalCrear = () => {
  modoEdicion.value = false
  form.value = { ...formVacio }
  errores.value = {}
  modalFormulario.value = true
}

const abrirModalEditar = (contador) => {
  modoEdicion.value = true
  contadorSeleccionado.value = contador
  form.value = { ...contador }
  errores.value = {}
  modalFormulario.value = true
}

const abrirClientes = (contador) => {
  contadorSeleccionado.value = contador
  modalClientes.value = true
}

const confirmarEliminar = (contador) => {
  contadorAEliminar.value = contador
  modalEliminar.value = true
}

const abrirMapa = async (contador) => {
  contadorSeleccionado.value = contador
  modalMapa.value = true

  await nextTick()

  if (mapaInstancia) {
    mapaInstancia.remove()
    mapaInstancia = null
  }

  mapaInstancia = L.map('mapa').setView(
    [contador.latitud, contador.longitud], 16
  )

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapaInstancia)

  L.marker([contador.latitud, contador.longitud])
    .addTo(mapaInstancia)
    .bindPopup(`<b>${contador.numero_serie}</b><br>${contador.direccion_fisica}`)
    .openPopup()
}

const cerrarModal = () => {
  if (mapaInstancia) {
    mapaInstancia.remove()
    mapaInstancia = null
  }
  modalFormulario.value = false
  modalClientes.value = false
  modalEliminar.value = false
  modalMapa.value = false
  contadorSeleccionado.value = null
  contadorAEliminar.value = null
}

// --- Validación ---
const validar = () => {
  const e = {}
  if (!form.value.numero_serie || form.value.numero_serie.length < 5) e.numero_serie = 'Mínimo 5 caracteres'
  if (!form.value.cups_poliza) e.cups_poliza = 'El CUPS es obligatorio'
  if (!form.value.tipo_suministro) e.tipo_suministro = 'Selecciona un tipo'
  if (!form.value.marca) e.marca = 'La marca es obligatoria'
  if (!form.value.modelo) e.modelo = 'El modelo es obligatorio'
  if (!form.value.version_firmware) e.version_firmware = 'La versión es obligatoria'
  if (!form.value.direccion_fisica) e.direccion_fisica = 'La dirección es obligatoria'
  if (form.value.latitud === null || form.value.latitud === '') e.latitud = 'La latitud es obligatoria'
  else if (form.value.latitud < -90 || form.value.latitud > 90) e.latitud = 'Entre -90 y 90'
  if (form.value.longitud === null || form.value.longitud === '') e.longitud = 'La longitud es obligatoria'
  else if (form.value.longitud < -180 || form.value.longitud > 180) e.longitud = 'Entre -180 y 180'
  errores.value = e
  return Object.keys(e).length === 0
}

// --- Acciones ---
const guardarContador = () => {
  if (!validar()) return
  if (modoEdicion.value) {
    const idx = contadores.value.findIndex(c => c.id === contadorSeleccionado.value.id)
    contadores.value[idx] = { ...contadores.value[idx], ...form.value }
  } else {
    contadores.value.push({ id: Date.now().toString(), ...form.value, clientes: [] })
  }
  cerrarModal()
}

const eliminarContador = () => {
  contadores.value = contadores.value.filter(c => c.id !== contadorAEliminar.value.id)
  cerrarModal()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.contadores {
  min-height: 100vh;
  background: #080c14;
  padding: 2rem;
  font-family: 'DM Sans', sans-serif;
  color: #e8f4ff;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.page-title { font-size: 1.6rem; font-weight: 600; margin: 0; }
.page-sub { font-size: 0.8rem; color: #4a6080; margin: 0.2rem 0 0; }

/* Botones */
.btn-primary {
  display: flex; align-items: center; gap: 0.4rem;
  background: linear-gradient(135deg, #00d4ff, #0077ff);
  color: white; border: none; padding: 0.6rem 1.2rem;
  border-radius: 8px; font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s;
}
.btn-primary:hover { opacity: 0.85; }
.btn-secondary {
  background: rgba(255,255,255,0.06); color: #a8c8e8;
  border: 1px solid rgba(255,255,255,0.1); padding: 0.6rem 1.2rem;
  border-radius: 8px; font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; cursor: pointer; transition: background 0.2s;
}
.btn-secondary:hover { background: rgba(255,255,255,0.1); }
.btn-danger {
  background: rgba(255,23,68,0.15); color: #ff1744;
  border: 1px solid rgba(255,23,68,0.3); padding: 0.6rem 1.2rem;
  border-radius: 8px; font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; cursor: pointer; transition: background 0.2s;
}
.btn-danger:hover { background: rgba(255,23,68,0.25); }

/* Filtros */
.filtros {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  align-items: center;
}

.search-bar {
  display: flex; align-items: center; gap: 0.75rem;
  background: #0e1420; border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px; padding: 0.6rem 1rem; flex: 1; min-width: 200px;
}
.search-bar svg { width: 18px; height: 18px; color: #4a6080; flex-shrink: 0; }
.search-input {
  background: none; border: none; outline: none;
  color: #e8f4ff; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; width: 100%;
}
.search-input::placeholder { color: #4a6080; }

.filtro-chips { display: flex; gap: 0.4rem; }

.chip {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #4a6080; padding: 0.35rem 0.85rem;
  border-radius: 99px; font-size: 0.78rem;
  cursor: pointer; transition: all 0.2s;
  font-family: 'DM Sans', sans-serif;
}
.chip:hover { background: rgba(255,255,255,0.08); color: #a8c8e8; }
.chip.active { background: rgba(0,212,255,0.12); border-color: rgba(0,212,255,0.3); color: #00d4ff; }
.chip.estado.activo.active { background: rgba(0,230,118,0.12); border-color: rgba(0,230,118,0.3); color: #00e676; }
.chip.estado.averiado.active { background: rgba(255,145,0,0.12); border-color: rgba(255,145,0,0.3); color: #ff9100; }
.chip.estado.saboteado.active { background: rgba(255,23,68,0.12); border-color: rgba(255,23,68,0.3); color: #ff1744; }

/* Tabla */
.table-wrap {
  background: #0e1420; border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px; overflow: auto;
}
.tabla { width: 100%; border-collapse: collapse; min-width: 900px; }
.tabla thead tr {
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.tabla th {
  text-align: left; padding: 0.9rem 1rem;
  font-size: 0.72rem; font-weight: 600; color: #4a6080;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.tabla-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.tabla-row:last-child { border-bottom: none; }
.tabla-row:hover { background: rgba(255,255,255,0.02); }
.tabla td { padding: 0.85rem 1rem; font-size: 0.85rem; }

.tipo-badge {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 500;
}
.tipo-badge.electricidad { background: rgba(0,212,255,0.12); color: #00d4ff; border: 1px solid rgba(0,212,255,0.2); }
.tipo-badge.agua { background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.2); }
.tipo-badge.gas { background: rgba(255,145,0,0.12); color: #ff9100; border: 1px solid rgba(255,145,0,0.2); }

.mono { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.text-muted { color: #4a6080; }
.dir { color: #a8c8e8; font-size: 0.8rem; max-width: 160px; }

.marca { display: block; font-weight: 500; color: #e8f4ff; font-size: 0.82rem; }
.modelo { display: block; color: #4a6080; font-size: 0.72rem; margin-top: 2px; }

.estado-badge {
  display: inline-block; padding: 0.25rem 0.75rem;
  border-radius: 99px; font-size: 0.72rem; font-weight: 500;
}
.estado-badge.activo { background: rgba(0,230,118,0.12); color: #00e676; }
.estado-badge.averiado { background: rgba(255,145,0,0.12); color: #ff9100; }
.estado-badge.saboteado { background: rgba(255,23,68,0.12); color: #ff1744; }

.btn-clientes {
  display: flex; align-items: center; gap: 0.35rem;
  background: rgba(255,255,255,0.05); color: #a8c8e8;
  border: 1px solid rgba(255,255,255,0.08); padding: 0.3rem 0.7rem;
  border-radius: 6px; font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem; cursor: pointer; transition: background 0.2s;
}
.btn-clientes:hover { background: rgba(255,255,255,0.1); }
.btn-clientes svg { width: 14px; height: 14px; }

.acciones { display: flex; gap: 0.4rem; }
.btn-icon {
  width: 32px; height: 32px; border-radius: 6px; border: none;
  cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s;
}
.btn-icon svg { width: 15px; height: 15px; }
.btn-icon.edit { background: rgba(0,212,255,0.08); color: #00d4ff; }
.btn-icon.edit:hover { background: rgba(0,212,255,0.18); }
.btn-icon.delete { background: rgba(255,23,68,0.08); color: #ff1744; }
.btn-icon.delete:hover { background: rgba(255,23,68,0.18); }

.empty-row { text-align: center; color: #4a6080; padding: 2rem; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px); display: flex; align-items: center;
  justify-content: center; z-index: 200; padding: 1rem;
}
.modal {
  background: #0e1420; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px; width: 100%; max-width: 560px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6); max-height: 90vh; overflow-y: auto;
}
.modal-lg { max-width: 720px; }
.modal-sm { max-width: 400px; }

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.06);
  position: sticky; top: 0; background: #0e1420; z-index: 1;
}
.modal-title { font-size: 1rem; font-weight: 600; margin: 0; }
.btn-close {
  background: none; border: none; color: #4a6080;
  font-size: 1rem; cursor: pointer; padding: 0.25rem; line-height: 1; transition: color 0.2s;
}
.btn-close:hover { color: #e8f4ff; }
.modal-body { padding: 1.5rem; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 0.75rem;
  padding: 1.25rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.06);
}

/* Formulario */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group.full { grid-column: 1 / -1; }
.form-group label {
  font-size: 0.75rem; color: #4a6080; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.form-group input, .form-group select {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; padding: 0.6rem 0.85rem; color: #e8f4ff;
  font-family: 'DM Sans', sans-serif; font-size: 0.875rem; outline: none; transition: border-color 0.2s;
}
.form-group select option { background: #0e1420; }
.form-group input:focus, .form-group select:focus { border-color: #00d4ff; }
.form-group input.error, .form-group select.error { border-color: #ff1744; }
.form-group input:disabled { opacity: 0.5; cursor: not-allowed; }
.error-msg { font-size: 0.7rem; color: #ff1744; }

/* Clientes lista */
.clientes-list { display: flex; flex-direction: column; gap: 0.6rem; }
.cliente-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.7rem 0.85rem; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
}
.avatar {
  width: 34px; height: 34px; border-radius: 8px;
  background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,119,255,0.2));
  color: #00d4ff; display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}
.cliente-info { display: flex; flex-direction: column; }
.cliente-nombre { font-size: 0.85rem; color: #e8f4ff; font-weight: 500; }
.cliente-email { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #4a6080; }

.empty-state { text-align: center; color: #4a6080; font-size: 0.85rem; padding: 1rem; }
.confirm-text { color: #a8c8e8; font-size: 0.9rem; line-height: 1.6; margin: 0; }
.confirm-text strong { color: #e8f4ff; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95) translateY(10px); }

.btn-mapa {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  margin-left: 0.4rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.btn-mapa:hover { opacity: 1; }
</style>