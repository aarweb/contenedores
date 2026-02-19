<template>
  <div class="clientes">

    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Clientes</h1>
        <p class="page-sub">{{ clientesFiltrados.length }} clientes encontrados</p>
      </div>
      <button class="btn-primary" @click="abrirModalCrear">
        <span>+</span> Nuevo cliente
      </button>
    </div>

    <!-- Buscador -->
    <div class="search-bar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar por nombre o email..."
        class="search-input"
      />
    </div>

    <!-- Tabla -->
    <div class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Dirección</th>
            <th>Registro</th>
            <th>Contadores</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="clientesFiltrados.length === 0">
            <td colspan="7" class="empty-row">No se encontraron clientes</td>
          </tr>
          <tr v-for="cliente in clientesFiltrados" :key="cliente.id" class="tabla-row">
            <td>
              <div class="cliente-nombre">
                <div class="avatar">{{ iniciales(cliente) }}</div>
                <div>
                  <span class="nombre-full">{{ cliente.nombre }} {{ cliente.apellidos }}</span>
                </div>
              </div>
            </td>
            <td class="mono">{{ cliente.email }}</td>
            <td class="mono">{{ cliente.telefono }}</td>
            <td class="dir">{{ cliente.direccion_facturacion }}</td>
            <td class="mono text-muted">{{ formatFecha(cliente.fecha_registro) }}</td>
            <td>
              <button class="btn-contadores" @click="abrirContadores(cliente)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>
                </svg>
                {{ cliente.contadores?.length ?? 0 }}
              </button>
            </td>
            <td>
              <div class="acciones">
                <button class="btn-icon edit" @click="abrirModalEditar(cliente)" title="Editar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="btn-icon delete" @click="confirmarEliminar(cliente)" title="Eliminar">
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

    <!-- MODAL: Crear / Editar cliente -->
    <Transition name="modal">
      <div v-if="modalFormulario" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">{{ modoEdicion ? 'Editar cliente' : 'Nuevo cliente' }}</h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>Nombre</label>
                <input v-model="form.nombre" type="text" placeholder="Juan" :class="{ error: errores.nombre }" />
                <span v-if="errores.nombre" class="error-msg">{{ errores.nombre }}</span>
              </div>
              <div class="form-group">
                <label>Apellidos</label>
                <input v-model="form.apellidos" type="text" placeholder="García López" :class="{ error: errores.apellidos }" />
                <span v-if="errores.apellidos" class="error-msg">{{ errores.apellidos }}</span>
              </div>
              <div class="form-group full">
                <label>Email</label>
                <input v-model="form.email" type="email" placeholder="juan@email.com" :class="{ error: errores.email }" />
                <span v-if="errores.email" class="error-msg">{{ errores.email }}</span>
              </div>
              <div class="form-group">
                <label>Teléfono</label>
                <input v-model="form.telefono" type="text" placeholder="612 345 678" :class="{ error: errores.telefono }" />
                <span v-if="errores.telefono" class="error-msg">{{ errores.telefono }}</span>
              </div>
              <div class="form-group full">
                <label>Dirección de facturación</label>
                <input v-model="form.direccion_facturacion" type="text" placeholder="Calle Mayor 1, Madrid" :class="{ error: errores.direccion_facturacion }" />
                <span v-if="errores.direccion_facturacion" class="error-msg">{{ errores.direccion_facturacion }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button class="btn-primary" @click="guardarCliente">
              {{ modoEdicion ? 'Guardar cambios' : 'Crear cliente' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Contadores del cliente -->
    <Transition name="modal">
      <div v-if="modalContadores" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">
              Contadores de {{ clienteSeleccionado?.nombre }} {{ clienteSeleccionado?.apellidos }}
            </h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <div v-if="!clienteSeleccionado?.contadores?.length" class="empty-state">
              Este cliente no tiene contadores asignados
            </div>
            <div v-else class="contadores-list">
              <div class="contador-item" v-for="c in clienteSeleccionado.contadores" :key="c.id">
                <span class="contador-emoji">{{ emojiTipo(c.tipo) }}</span>
                <div class="contador-info">
                  <span class="contador-serie">{{ c.numero_serie }}</span>
                  <span class="contador-tipo">{{ c.tipo }}</span>
                </div>
                <span class="contador-estado" :class="c.estado.toLowerCase()">{{ c.estado }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cerrar</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: Confirmar eliminar -->
    <Transition name="modal">
      <div v-if="modalEliminar" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2 class="modal-title">Eliminar cliente</h2>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>
          <div class="modal-body">
            <p class="confirm-text">
              ¿Estás seguro de que quieres eliminar a
              <strong>{{ clienteAEliminar?.nombre }} {{ clienteAEliminar?.apellidos }}</strong>?
              Esta acción no se puede deshacer.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button class="btn-danger" @click="eliminarCliente">Eliminar</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// --- Estado ---
const busqueda = ref('')
const modalFormulario = ref(false)
const modalContadores = ref(false)
const modalEliminar = ref(false)
const modoEdicion = ref(false)
const clienteSeleccionado = ref(null)
const clienteAEliminar = ref(null)

const form = ref({
  nombre: '', apellidos: '', email: '', telefono: '', direccion_facturacion: ''
})
const errores = ref({})

// Datos de ejemplo — se reemplazarán con llamadas a la API
const clientes = ref([
  {
    id: '1', nombre: 'Juan', apellidos: 'García López', email: 'juan@email.com',
    telefono: '612345678', direccion_facturacion: 'Calle Mayor 1, Madrid',
    fecha_registro: '2024-01-15T10:00:00',
    contadores: [
      { id: 'c1', numero_serie: 'SN-2024-001', tipo: 'Electricidad', estado: 'Activo' },
      { id: 'c2', numero_serie: 'SN-2024-002', tipo: 'Agua', estado: 'Activo' },
    ]
  },
  {
    id: '2', nombre: 'María', apellidos: 'Martínez Ruiz', email: 'maria@email.com',
    telefono: '698765432', direccion_facturacion: 'Av. Libertad 24, Valencia',
    fecha_registro: '2024-02-20T09:30:00',
    contadores: [
      { id: 'c3', numero_serie: 'SN-2024-045', tipo: 'Gas', estado: 'Averiado' },
    ]
  },
  {
    id: '3', nombre: 'Carlos', apellidos: 'Fernández Díaz', email: 'carlos@email.com',
    telefono: '655112233', direccion_facturacion: 'Plaza España 3, Sevilla',
    fecha_registro: '2024-03-10T14:00:00',
    contadores: []
  },
])

// --- Computed ---
const clientesFiltrados = computed(() => {
  const q = busqueda.value.toLowerCase()
  if (!q) return clientes.value
  return clientes.value.filter(c =>
    `${c.nombre} ${c.apellidos}`.toLowerCase().includes(q) ||
    c.email.toLowerCase().includes(q)
  )
})

// --- Helpers ---
const iniciales = (c) => `${c.nombre[0]}${c.apellidos[0]}`.toUpperCase()
const formatFecha = (f) => new Date(f).toLocaleDateString('es-ES')
const emojiTipo = (t) => ({ Electricidad: '⚡', Agua: '💧', Gas: '🔥' }[t] ?? '📊')

// --- Modales ---
const abrirModalCrear = () => {
  modoEdicion.value = false
  form.value = { nombre: '', apellidos: '', email: '', telefono: '', direccion_facturacion: '' }
  errores.value = {}
  modalFormulario.value = true
}

const abrirModalEditar = (cliente) => {
  modoEdicion.value = true
  clienteSeleccionado.value = cliente
  form.value = { ...cliente }
  errores.value = {}
  modalFormulario.value = true
}

const abrirContadores = (cliente) => {
  clienteSeleccionado.value = cliente
  modalContadores.value = true
}

const confirmarEliminar = (cliente) => {
  clienteAEliminar.value = cliente
  modalEliminar.value = true
}

const cerrarModal = () => {
  modalFormulario.value = false
  modalContadores.value = false
  modalEliminar.value = false
  clienteSeleccionado.value = null
  clienteAEliminar.value = null
}

// --- Validación ---
const validar = () => {
  const e = {}
  if (!form.value.nombre) e.nombre = 'El nombre es obligatorio'
  if (!form.value.apellidos) e.apellidos = 'Los apellidos son obligatorios'
  if (!form.value.email) e.email = 'El email es obligatorio'
  else if (!/\S+@\S+\.\S+/.test(form.value.email)) e.email = 'El email no es válido'
  if (!form.value.telefono) e.telefono = 'El teléfono es obligatorio'
  if (!form.value.direccion_facturacion) e.direccion_facturacion = 'La dirección es obligatoria'
  errores.value = e
  return Object.keys(e).length === 0
}

// --- Acciones (se reemplazarán con llamadas a la API) ---
const guardarCliente = () => {
  if (!validar()) return
  if (modoEdicion.value) {
    const idx = clientes.value.findIndex(c => c.id === clienteSeleccionado.value.id)
    clientes.value[idx] = { ...clientes.value[idx], ...form.value }
  } else {
    clientes.value.push({
      id: Date.now().toString(),
      ...form.value,
      fecha_registro: new Date().toISOString(),
      contadores: []
    })
  }
  cerrarModal()
}

const eliminarCliente = () => {
  clientes.value = clientes.value.filter(c => c.id !== clienteAEliminar.value.id)
  cerrarModal()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600&display=swap');

.clientes {
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
  margin-bottom: 1.5rem;
}
.page-title { font-size: 1.6rem; font-weight: 600; margin: 0; }
.page-sub { font-size: 0.8rem; color: #4a6080; margin: 0.2rem 0 0; }

/* Botones */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #00d4ff, #0077ff);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-primary:hover { opacity: 0.85; }

.btn-secondary {
  background: rgba(255,255,255,0.06);
  color: #a8c8e8;
  border: 1px solid rgba(255,255,255,0.1);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-secondary:hover { background: rgba(255,255,255,0.1); }

.btn-danger {
  background: rgba(255,23,68,0.15);
  color: #ff1744;
  border: 1px solid rgba(255,23,68,0.3);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-danger:hover { background: rgba(255,23,68,0.25); }

/* Search */
.search-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #0e1420;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 0.6rem 1rem;
  margin-bottom: 1.5rem;
}
.search-bar svg { width: 18px; height: 18px; color: #4a6080; flex-shrink: 0; }
.search-input {
  background: none;
  border: none;
  outline: none;
  color: #e8f4ff;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  width: 100%;
}
.search-input::placeholder { color: #4a6080; }

/* Tabla */
.table-wrap {
  background: #0e1420;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  overflow: hidden;
}

.tabla { width: 100%; border-collapse: collapse; }

.tabla thead tr {
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.tabla th {
  text-align: left;
  padding: 0.9rem 1rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #4a6080;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.tabla-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.tabla-row:last-child { border-bottom: none; }
.tabla-row:hover { background: rgba(255,255,255,0.02); }

.tabla td { padding: 0.85rem 1rem; font-size: 0.85rem; }

.cliente-nombre { display: flex; align-items: center; gap: 0.75rem; }

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,119,255,0.2));
  color: #00d4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  flex-shrink: 0;
}

.nombre-full { font-weight: 500; color: #e8f4ff; }
.mono { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.text-muted { color: #4a6080; }
.dir { color: #a8c8e8; font-size: 0.8rem; max-width: 180px; }

.empty-row { text-align: center; color: #4a6080; padding: 2rem; }

/* Btn contadores */
.btn-contadores {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(0,212,255,0.08);
  color: #00d4ff;
  border: 1px solid rgba(0,212,255,0.2);
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-contadores:hover { background: rgba(0,212,255,0.15); }
.btn-contadores svg { width: 14px; height: 14px; }

/* Acciones */
.acciones { display: flex; gap: 0.4rem; }
.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.btn-icon svg { width: 15px; height: 15px; }
.btn-icon.edit { background: rgba(0,212,255,0.08); color: #00d4ff; }
.btn-icon.edit:hover { background: rgba(0,212,255,0.18); }
.btn-icon.delete { background: rgba(255,23,68,0.08); color: #ff1744; }
.btn-icon.delete:hover { background: rgba(255,23,68,0.18); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.modal {
  background: #0e1420;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6);
}

.modal-sm { max-width: 400px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.modal-title { font-size: 1rem; font-weight: 600; margin: 0; }

.btn-close {
  background: none;
  border: none;
  color: #4a6080;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  transition: color 0.2s;
}
.btn-close:hover { color: #e8f4ff; }

.modal-body { padding: 1.5rem; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.06);
}

/* Formulario */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group.full { grid-column: 1 / -1; }

.form-group label { font-size: 0.75rem; color: #4a6080; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }

.form-group input {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  color: #e8f4ff;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus { border-color: #00d4ff; }
.form-group input.error { border-color: #ff1744; }
.error-msg { font-size: 0.7rem; color: #ff1744; }

/* Contadores lista */
.contadores-list { display: flex; flex-direction: column; gap: 0.6rem; }
.contador-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.85rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
}
.contador-emoji { font-size: 1.1rem; }
.contador-info { flex: 1; display: flex; flex-direction: column; }
.contador-serie { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #e8f4ff; }
.contador-tipo { font-size: 0.7rem; color: #4a6080; margin-top: 2px; }
.contador-estado {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 99px;
}
.contador-estado.activo { background: rgba(0,230,118,0.15); color: #00e676; }
.contador-estado.averiado { background: rgba(255,145,0,0.15); color: #ff9100; }
.contador-estado.saboteado { background: rgba(255,23,68,0.15); color: #ff1744; }

.empty-state { text-align: center; color: #4a6080; font-size: 0.85rem; padding: 1rem; }

.confirm-text { color: #a8c8e8; font-size: 0.9rem; line-height: 1.6; margin: 0; }
.confirm-text strong { color: #e8f4ff; }

/* Transición modal */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95) translateY(10px); }
</style>