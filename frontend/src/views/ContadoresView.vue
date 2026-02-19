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
        <button v-for="tipo in tiposFiltro" :key="tipo.value"
          class="chip" :class="{ active: filtroTipo === tipo.value }"
          @click="filtroTipo = filtroTipo === tipo.value ? null : tipo.value">
          {{ tipo.emoji }} {{ tipo.label }}
        </button>
      </div>
      <div class="filtro-chips">
        <button v-for="estado in estadosFiltro" :key="estado.value"
          class="chip estado" :class="[{ active: filtroEstado === estado.value }, estado.value.toLowerCase()]"
          @click="filtroEstado = filtroEstado === estado.value ? null : estado.value">
          {{ estado.label }}
        </button>
      </div>
    </div>

    <!-- Error global -->
    <div v-if="errorGlobal" class="error-banner">
      ⚠️ {{ errorGlobal }}
      <button @click="errorGlobal = null">✕</button>
    </div>

    <!-- Tabla -->
    <div class="table-wrap">
      <div v-if="cargando" class="loading-state">
        <div class="spinner" /> Cargando contadores...
      </div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Tipo</th><th>Nº Serie</th><th>CUPS / Póliza</th>
            <th>Marca / Modelo</th><th>Dirección</th>
            <th>Estado</th><th>Clientes</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="contadoresFiltrados.length === 0">
            <td colspan="8" class="empty-row">No se encontraron contadores</td>
          </tr>
          <tr v-for="contador in contadoresFiltrados" :key="contador._id" class="tabla-row">
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
              <span class="estado-badge" :class="contador.estado.toLowerCase()">{{ contador.estado }}</span>
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
            <div v-if="errorModal" class="error-banner small">⚠️ {{ errorModal }}</div>
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
                <select v-model="form.tipo_suministro" :disabled="modoEdicion" :class="{ error: errores.tipo_suministro }">
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
              <!-- Selector de ubicación -->
              <div class="form-group full">
                <label>Ubicación</label>

                <!-- Buscador de dirección -->
                <div class="geo-search">
                  <input
                    v-model="geocodeBusqueda"
                    type="text"
                    placeholder="Buscar dirección para centrar el mapa..."
                    class="geo-input"
                    @keyup.enter="geocodificar"
                  />
                  <button class="btn-geocode" @click="geocodificar" :disabled="geocodeCargando">
                    <span v-if="geocodeCargando" class="spinner-sm" />
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:14px;height:14px">
                      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                    Buscar
                  </button>
                </div>
                <p v-if="geocodeError" class="error-msg">{{ geocodeError }}</p>

                <!-- Mapa del formulario -->
                <div class="mapa-form-wrap" :class="{ 'has-error': errores.latitud || errores.longitud }">
                  <div id="mapa-form" class="mapa-form" />
                  <div class="mapa-hint">📍 Haz clic en el mapa o arrastra el marcador para elegir la ubicación exacta</div>
                </div>

                <!-- Coordenadas manuales -->
                <div class="coords-row">
                  <div class="coord-group">
                    <label>Latitud</label>
                    <input
                      v-model.number="form.latitud" type="number"
                      placeholder="40.4167" step="0.0001"
                      :class="{ error: errores.latitud }"
                      @change="actualizarMarcadorForm"
                    />
                    <span v-if="errores.latitud" class="error-msg">{{ errores.latitud }}</span>
                  </div>
                  <div class="coord-group">
                    <label>Longitud</label>
                    <input
                      v-model.number="form.longitud" type="number"
                      placeholder="-3.7033" step="0.0001"
                      :class="{ error: errores.longitud }"
                      @change="actualizarMarcadorForm"
                    />
                    <span v-if="errores.longitud" class="error-msg">{{ errores.longitud }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal" :disabled="guardando">Cancelar</button>
            <button class="btn-primary" @click="guardarContador" :disabled="guardando">
              <span v-if="guardando" class="spinner-sm" />
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
            <h2 class="modal-title">Clientes de {{ contadorSeleccionado?.numero_serie }}</h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <div v-if="cargandoClientes" class="loading-state small">
              <div class="spinner" /> Cargando clientes...
            </div>
            <div v-else-if="!clientesModal.length" class="empty-state">
              Este contador no tiene clientes asignados
            </div>
            <div v-else class="clientes-list">
              <div class="cliente-item" v-for="c in clientesModal" :key="c._id">
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
            <button class="btn-secondary" @click="cerrarModal" :disabled="guardando">Cancelar</button>
            <button class="btn-danger" @click="eliminarContador" :disabled="guardando">
              <span v-if="guardando" class="spinner-sm" />
              Eliminar
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api, contadoresService, clientesService } from '@/services/api'

import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
L.Marker.prototype.options.icon = L.icon({
  iconUrl, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41]
})

// --- Estado ---
const contadores = ref([])
const cargando = ref(false)
const guardando = ref(false)
const errorGlobal = ref(null)
const errorModal = ref(null)
const busqueda = ref('')
const filtroTipo = ref(null)
const filtroEstado = ref(null)
const modalFormulario = ref(false)
const modalClientes = ref(false)
const modalEliminar = ref(false)
const modalMapa = ref(false)
const cargandoClientes = ref(false)
const clientesModal = ref([])
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

// --- Estado mapa formulario ---
let mapaFormInstancia = null
let marcadorForm = null
const geocodeBusqueda = ref('')
const geocodeCargando = ref(false)
const geocodeError = ref(null)

onMounted(cargarContadores)

async function cargarContadores() {
  cargando.value = true
  errorGlobal.value = null
  try {
    contadores.value = await contadoresService.getAll(0, 100)
  } catch (e) {
    errorGlobal.value = e.message
  } finally {
    cargando.value = false
  }
}

const contadoresFiltrados = computed(() => {
  return contadores.value.filter(c => {
    const q = busqueda.value.toLowerCase()
    const matchBusqueda = !q || c.numero_serie.toLowerCase().includes(q) || c.cups_poliza.toLowerCase().includes(q)
    const matchTipo = !filtroTipo.value || c.tipo_suministro === filtroTipo.value
    const matchEstado = !filtroEstado.value || c.estado === filtroEstado.value
    return matchBusqueda && matchTipo && matchEstado
  })
})

const emojiTipo = (t) => ({ Electricidad: '⚡', Agua: '💧', Gas: '🔥' }[t] ?? '📊')

const abrirModalCrear = () => {
  modoEdicion.value = false
  form.value = { ...formVacio }
  errores.value = {}
  errorModal.value = null
  geocodeBusqueda.value = ''
  geocodeError.value = null
  modalFormulario.value = true
  nextTick(() => iniciarMapaForm(40.4167, -3.7033, false))
}

const abrirModalEditar = (contador) => {
  modoEdicion.value = true
  contadorSeleccionado.value = contador
  form.value = {
    numero_serie: contador.numero_serie, cups_poliza: contador.cups_poliza,
    marca: contador.marca, modelo: contador.modelo,
    version_firmware: contador.version_firmware, direccion_fisica: contador.direccion_fisica,
    tipo_suministro: contador.tipo_suministro, estado: contador.estado,
    latitud: contador.latitud, longitud: contador.longitud,
  }
  errores.value = {}
  errorModal.value = null
  geocodeBusqueda.value = ''
  geocodeError.value = null
  modalFormulario.value = true
  nextTick(() => iniciarMapaForm(contador.latitud, contador.longitud, true))
}

function iniciarMapaForm(lat, lng, conMarcador) {
  if (mapaFormInstancia) { mapaFormInstancia.remove(); mapaFormInstancia = null; marcadorForm = null }

  mapaFormInstancia = L.map('mapa-form').setView([lat, lng], conMarcador ? 16 : 6)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapaFormInstancia)

  if (conMarcador) {
    marcadorForm = L.marker([lat, lng], { draggable: true }).addTo(mapaFormInstancia)
    marcadorForm.on('dragend', (e) => {
      const pos = e.target.getLatLng()
      form.value.latitud = parseFloat(pos.lat.toFixed(6))
      form.value.longitud = parseFloat(pos.lng.toFixed(6))
    })
  }

  // Clic en el mapa coloca/mueve el marcador
  mapaFormInstancia.on('click', (e) => {
    form.value.latitud = parseFloat(e.latlng.lat.toFixed(6))
    form.value.longitud = parseFloat(e.latlng.lng.toFixed(6))
    if (marcadorForm) {
      marcadorForm.setLatLng(e.latlng)
    } else {
      marcadorForm = L.marker(e.latlng, { draggable: true }).addTo(mapaFormInstancia)
      marcadorForm.on('dragend', (ev) => {
        const pos = ev.target.getLatLng()
        form.value.latitud = parseFloat(pos.lat.toFixed(6))
        form.value.longitud = parseFloat(pos.lng.toFixed(6))
      })
    }
  })
}

function actualizarMarcadorForm() {
  if (!mapaFormInstancia || !form.value.latitud || !form.value.longitud) return
  const pos = [form.value.latitud, form.value.longitud]
  if (marcadorForm) {
    marcadorForm.setLatLng(pos)
  } else {
    marcadorForm = L.marker(pos, { draggable: true }).addTo(mapaFormInstancia)
    marcadorForm.on('dragend', (e) => {
      const p = e.target.getLatLng()
      form.value.latitud = parseFloat(p.lat.toFixed(6))
      form.value.longitud = parseFloat(p.lng.toFixed(6))
    })
  }
  mapaFormInstancia.setView(pos, 16)
}

async function geocodificar() {
  if (!geocodeBusqueda.value.trim()) return
  geocodeCargando.value = true
  geocodeError.value = null
  try {
    const data = await api.get(`/geocode/?q=${encodeURIComponent(geocodeBusqueda.value)}&limit=1`)
    if (!data.length) { geocodeError.value = 'No se encontró ninguna dirección'; return }
    const { lat, lon } = data[0]
    form.value.latitud = parseFloat(parseFloat(lat).toFixed(6))
    form.value.longitud = parseFloat(parseFloat(lon).toFixed(6))
    actualizarMarcadorForm()
  } catch {
    geocodeError.value = 'Error al buscar la dirección'
  } finally {
    geocodeCargando.value = false
  }
}

const abrirClientes = async (contador) => {
  contadorSeleccionado.value = contador
  modalClientes.value = true
  cargandoClientes.value = true
  clientesModal.value = []
  try {
    const todos = await clientesService.getAll(0, 100)
    clientesModal.value = todos.filter(c => contador.clientes?.includes(c._id))
  } catch (e) {
    errorGlobal.value = e.message
  } finally {
    cargandoClientes.value = false
  }
}

const confirmarEliminar = (contador) => {
  contadorAEliminar.value = contador
  modalEliminar.value = true
}

const abrirMapa = async (contador) => {
  contadorSeleccionado.value = contador
  modalMapa.value = true
  await nextTick()
  if (mapaInstancia) { mapaInstancia.remove(); mapaInstancia = null }
  mapaInstancia = L.map('mapa').setView([contador.latitud, contador.longitud], 16)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapaInstancia)
  L.marker([contador.latitud, contador.longitud])
    .addTo(mapaInstancia)
    .bindPopup(`<b>${contador.numero_serie}</b><br>${contador.direccion_fisica}`)
    .openPopup()
}

const cerrarModal = () => {
  if (mapaInstancia) { mapaInstancia.remove(); mapaInstancia = null }
  if (mapaFormInstancia) { mapaFormInstancia.remove(); mapaFormInstancia = null; marcadorForm = null }
  modalFormulario.value = false
  modalClientes.value = false
  modalEliminar.value = false
  modalMapa.value = false
  contadorSeleccionado.value = null
  contadorAEliminar.value = null
  clientesModal.value = []
  errorModal.value = null
}

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

const guardarContador = async () => {
  if (!validar()) return
  guardando.value = true
  errorModal.value = null
  try {
    if (modoEdicion.value) {
      await contadoresService.update(contadorSeleccionado.value._id, form.value)
    } else {
      await contadoresService.create(form.value)
    }
    await cargarContadores()
    cerrarModal()
  } catch (e) {
    errorModal.value = e.message
  } finally {
    guardando.value = false
  }
}

const eliminarContador = async () => {
  guardando.value = true
  try {
    await contadoresService.delete(contadorAEliminar.value._id)
    await cargarContadores()
    cerrarModal()
  } catch (e) {
    errorGlobal.value = e.message
    cerrarModal()
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.contadores { min-height: 100vh; background: #080c14; padding: 2rem; font-family: 'DM Sans', sans-serif; color: #e8f4ff; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 1.6rem; font-weight: 600; margin: 0; }
.page-sub { font-size: 0.8rem; color: #4a6080; margin: 0.2rem 0 0; }

.btn-primary { display: flex; align-items: center; gap: 0.4rem; background: linear-gradient(135deg, #00d4ff, #0077ff); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.btn-primary:hover:not(:disabled) { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: rgba(255,255,255,0.06); color: #a8c8e8; border: 1px solid rgba(255,255,255,0.1); padding: 0.6rem 1.2rem; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 0.85rem; cursor: pointer; transition: background 0.2s; }
.btn-secondary:hover:not(:disabled) { background: rgba(255,255,255,0.1); }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger { display: flex; align-items: center; gap: 0.4rem; background: rgba(255,23,68,0.15); color: #ff1744; border: 1px solid rgba(255,23,68,0.3); padding: 0.6rem 1.2rem; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 0.85rem; cursor: pointer; transition: background 0.2s; }
.btn-danger:hover:not(:disabled) { background: rgba(255,23,68,0.25); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.error-banner { display: flex; justify-content: space-between; align-items: center; background: rgba(255,23,68,0.1); border: 1px solid rgba(255,23,68,0.3); color: #ff1744; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; }
.error-banner button { background: none; border: none; color: #ff1744; cursor: pointer; font-size: 1rem; }
.error-banner.small { margin-bottom: 1rem; }

.loading-state { display: flex; align-items: center; gap: 0.75rem; color: #4a6080; padding: 3rem; justify-content: center; font-size: 0.85rem; }
.loading-state.small { padding: 1rem; }
.spinner { width: 20px; height: 20px; border: 2px solid rgba(0,212,255,0.2); border-top-color: #00d4ff; border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0; }
.spinner-sm { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.filtros { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; align-items: center; }
.search-bar { display: flex; align-items: center; gap: 0.75rem; background: #0e1420; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.6rem 1rem; flex: 1; min-width: 200px; }
.search-bar svg { width: 18px; height: 18px; color: #4a6080; flex-shrink: 0; }
.search-input { background: none; border: none; outline: none; color: #e8f4ff; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; width: 100%; }
.search-input::placeholder { color: #4a6080; }
.filtro-chips { display: flex; gap: 0.4rem; }
.chip { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #4a6080; padding: 0.35rem 0.85rem; border-radius: 99px; font-size: 0.78rem; cursor: pointer; transition: all 0.2s; font-family: 'DM Sans', sans-serif; }
.chip:hover { background: rgba(255,255,255,0.08); color: #a8c8e8; }
.chip.active { background: rgba(0,212,255,0.12); border-color: rgba(0,212,255,0.3); color: #00d4ff; }
.chip.estado.activo.active { background: rgba(0,230,118,0.12); border-color: rgba(0,230,118,0.3); color: #00e676; }
.chip.estado.averiado.active { background: rgba(255,145,0,0.12); border-color: rgba(255,145,0,0.3); color: #ff9100; }
.chip.estado.saboteado.active { background: rgba(255,23,68,0.12); border-color: rgba(255,23,68,0.3); color: #ff1744; }

.table-wrap { background: #0e1420; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; overflow: auto; }
.tabla { width: 100%; border-collapse: collapse; min-width: 900px; }
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
.dir { color: #a8c8e8; font-size: 0.8rem; max-width: 160px; }
.marca { display: block; font-weight: 500; color: #e8f4ff; font-size: 0.82rem; }
.modelo { display: block; color: #4a6080; font-size: 0.72rem; margin-top: 2px; }
.estado-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.72rem; font-weight: 500; }
.estado-badge.activo { background: rgba(0,230,118,0.12); color: #00e676; }
.estado-badge.averiado { background: rgba(255,145,0,0.12); color: #ff9100; }
.estado-badge.saboteado { background: rgba(255,23,68,0.12); color: #ff1744; }

.btn-clientes { display: flex; align-items: center; gap: 0.35rem; background: rgba(255,255,255,0.05); color: #a8c8e8; border: 1px solid rgba(255,255,255,0.08); padding: 0.3rem 0.7rem; border-radius: 6px; font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; cursor: pointer; transition: background 0.2s; }
.btn-clientes:hover { background: rgba(255,255,255,0.1); }
.btn-clientes svg { width: 14px; height: 14px; }
.acciones { display: flex; gap: 0.4rem; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.btn-icon svg { width: 15px; height: 15px; }
.btn-icon.edit { background: rgba(0,212,255,0.08); color: #00d4ff; }
.btn-icon.edit:hover { background: rgba(0,212,255,0.18); }
.btn-icon.delete { background: rgba(255,23,68,0.08); color: #ff1744; }
.btn-icon.delete:hover { background: rgba(255,23,68,0.18); }
.empty-row { text-align: center; color: #4a6080; padding: 2rem; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem; }
.modal { background: #0e1420; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; width: 100%; max-width: 560px; box-shadow: 0 24px 64px rgba(0,0,0,0.6); max-height: 90vh; overflow-y: auto; }
.modal-lg { max-width: 720px; }
.modal-sm { max-width: 400px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.06); position: sticky; top: 0; background: #0e1420; z-index: 1; }
.modal-title { font-size: 1rem; font-weight: 600; margin: 0; }
.btn-close { background: none; border: none; color: #4a6080; font-size: 1rem; cursor: pointer; padding: 0.25rem; line-height: 1; transition: color 0.2s; }
.btn-close:hover { color: #e8f4ff; }
.modal-body { padding: 1.5rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1.25rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.06); }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 0.75rem; color: #4a6080; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.form-group input, .form-group select { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 0.6rem 0.85rem; color: #e8f4ff; font-family: 'DM Sans', sans-serif; font-size: 0.875rem; outline: none; transition: border-color 0.2s; }
.form-group select option { background: #0e1420; }
.form-group input:focus, .form-group select:focus { border-color: #00d4ff; }
.form-group input.error, .form-group select.error { border-color: #ff1744; }
.form-group input:disabled, .form-group select:disabled { opacity: 0.5; cursor: not-allowed; }
.error-msg { font-size: 0.7rem; color: #ff1744; }

.clientes-list { display: flex; flex-direction: column; gap: 0.6rem; }
.cliente-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.7rem 0.85rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; }
.avatar { width: 34px; height: 34px; border-radius: 8px; background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,119,255,0.2)); color: #00d4ff; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; flex-shrink: 0; }
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

.btn-mapa { background: none; border: none; cursor: pointer; font-size: 0.9rem; margin-left: 0.4rem; opacity: 0.6; transition: opacity 0.2s; }
.btn-mapa:hover { opacity: 1; }

/* Mapa del formulario */
.geo-search {
  display: flex; gap: 0.5rem; margin-bottom: 0.5rem;
}
.geo-input {
  flex: 1; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; padding: 0.6rem 0.85rem; color: #e8f4ff;
  font-family: 'DM Sans', sans-serif; font-size: 0.85rem; outline: none; transition: border-color 0.2s;
}
.geo-input:focus { border-color: #00d4ff; }
.btn-geocode {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(0,212,255,0.1); color: #00d4ff;
  border: 1px solid rgba(0,212,255,0.25); padding: 0.6rem 1rem;
  border-radius: 8px; font-family: 'DM Sans', sans-serif;
  font-size: 0.8rem; cursor: pointer; white-space: nowrap; transition: background 0.2s;
}
.btn-geocode:hover:not(:disabled) { background: rgba(0,212,255,0.18); }
.btn-geocode:disabled { opacity: 0.5; cursor: not-allowed; }

.mapa-form-wrap {
  border-radius: 10px; overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 0.5rem;
  cursor: crosshair;
}
.mapa-form-wrap.has-error { border-color: #ff1744; }
.mapa-form { height: 280px; width: 100%; }
.mapa-hint {
  background: rgba(0,0,0,0.5); color: #4a6080;
  font-size: 0.7rem; padding: 0.4rem 0.75rem; text-align: center;
}

.coords-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.25rem;
}
.coord-group { display: flex; flex-direction: column; gap: 0.3rem; }
.coord-group label { font-size: 0.7rem; color: #4a6080; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.coord-group input {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px; padding: 0.5rem 0.75rem; color: #e8f4ff;
  font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; outline: none; transition: border-color 0.2s;
}
.coord-group input:focus { border-color: #00d4ff; }
.coord-group input.error { border-color: #ff1744; }
</style>