import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/',         redirect: '/calc' },
  { path: '/calc',     component: () => import('./views/CalcView.vue') },
  { path: '/profit',   component: () => import('./views/ProfitView.vue') },
  { path: '/cards',    component: () => import('./views/CardsView.vue') },
  { path: '/enhance',  component: () => import('./views/EnhanceView.vue') },
  { path: '/chars',    component: () => import('./views/CharSearchView.vue') },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
