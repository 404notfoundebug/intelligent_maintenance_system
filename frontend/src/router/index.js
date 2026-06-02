import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/login/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('../layout/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('../views/dashboard/Dashboard.vue'),
        meta: { title: '首页看板', icon: 'DataBoard' }
      },
      {
        path: 'devices',
        name: 'devices',
        component: () => import('../views/devices/DeviceList.vue'),
        meta: { title: '设备管理', icon: 'Cpu' }
      },
      {
        path: 'knowledge',
        name: 'knowledge',
        component: () => import('../views/knowledge/KnowledgeList.vue'),
        meta: { title: '知识库管理', icon: 'Collection' }
      },
      {
        path: 'qa',
        name: 'qa',
        component: () => import('../views/qa/RepairAdvice.vue'),
        meta: { title: '智能检修建议', icon: 'ChatLineRound' }
      },
      {
        path: 'inspections',
        name: 'inspections',
        component: () => import('../views/inspections/InspectionOrders.vue'),
        meta: { title: '点检工单', icon: 'Checked' }
      },
      {
        path: 'maintenance',
        name: 'maintenance',
        component: () => import('../views/maintenance/MaintenanceRecords.vue'),
        meta: { title: '维保记录', icon: 'DocumentChecked' }
      },
      {
        path: 'faults',
        name: 'faults',
        component: () => import('../views/faults/FaultReports.vue'),
        meta: { title: '故障上报', icon: 'Warning' }
      },
      {
        path: 'cases',
        name: 'cases',
        component: () => import('../views/cases/RepairCases.vue'),
        meta: { title: '检修案例', icon: 'Notebook' }
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('../views/users/UserList.vue'),
        meta: { title: '用户管理', icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!userStore.token) {
    userStore.restoreFromStorage()
  }

  if (to.meta.public && userStore.isLoggedIn) {
    return '/dashboard'
  }

  if (!to.meta.public && !userStore.isLoggedIn) {
    return `/login?redirect=${encodeURIComponent(to.fullPath)}`
  }

  document.title = `${to.meta.title || '系统'} - 电梯扶梯维保作业辅助系统`
  return true
})

export default router
