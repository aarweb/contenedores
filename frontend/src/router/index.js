import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import ClientesView from '@/views/ClientesView.vue'
import ContadoresView from '@/views/ContadoresView.vue'
import LecturasView from '@/views/LecturasView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',            redirect: '/dashboard' },
    { path: '/dashboard',   component: DashboardView  },
    { path: '/clientes',    component: ClientesView   },
    { path: '/contadores',  component: ContadoresView },
    { path: '/lecturas',    component: LecturasView   },
  ]
})