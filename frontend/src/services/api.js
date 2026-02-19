const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request(method, path, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) options.body = JSON.stringify(body)

  const res = await fetch(`${BASE_URL}${path}`, options)

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Error desconocido' }))
    throw new Error(error.detail ?? `Error ${res.status}`)
  }

  // 204 No Content no tiene cuerpo
  if (res.status === 204) return null

  return res.json()
}

export const api = {
  get:    (path)        => request('GET',    path),
  post:   (path, body)  => request('POST',   path, body),
  put:    (path, body)  => request('PUT',    path, body),
  delete: (path)        => request('DELETE', path),
}


export const clientesService = {
  getAll:   (skip = 0, limit = 20)    => api.get(`/clientes/?skip=${skip}&limit=${limit}`),
  getById:  (id)                       => api.get(`/clientes/${id}`),
  create:   (data)                     => api.post('/clientes/', data),
  update:   (id, data)                 => api.put(`/clientes/${id}`, data),
  delete:   (id)                       => api.delete(`/clientes/${id}`),
}


export const contadoresService = {
  getAll:   (skip = 0, limit = 20, tipo = null, estado = null) => {
    const params = new URLSearchParams({ skip, limit })
    if (tipo)   params.append('tipo',   tipo)
    if (estado) params.append('estado', estado)
    return api.get(`/contadores/?${params}`)
  },
  getById:          (id)              => api.get(`/contadores/${id}`),
  create:           (data)            => api.post('/contadores/', data),
  update:           (id, data)        => api.put(`/contadores/${id}`, data),
  delete:           (id)              => api.delete(`/contadores/${id}`),
  asignarCliente:   (contadorId, clienteId) => api.post(`/contadores/${contadorId}/clientes/${clienteId}`),
  desasignarCliente:(contadorId, clienteId) => api.delete(`/contadores/${contadorId}/clientes/${clienteId}`),
}


export const lecturasService = {
  create:           (data)            => api.post('/lecturas/', data),
  getByContador:    (contadorId, skip = 0, limit = 20) =>
                      api.get(`/lecturas/contador/${contadorId}?skip=${skip}&limit=${limit}`),
  getUltima:        (contadorId)      => api.get(`/lecturas/contador/${contadorId}/ultima`),
  getConsumo:       (contadorId, fechaInicio, fechaFin) =>
                      api.get(`/lecturas/contador/${contadorId}/consumo?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`),
}