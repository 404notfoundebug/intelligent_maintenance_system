import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRole } from '@/utils/auth'

// ---- 入口 ----
import EntryPage from '@/views/entry/EntryPage.vue'

// ---- 双端登录 ----
import AdminLogin from '@/views/admin/AdminLogin.vue'
import WorkerLogin from '@/views/worker/WorkerLogin.vue'

// ---- 布局 ----
import AdminLayout from '@/layout/AdminLayout.vue'
import WorkerLayout from '@/layout/WorkerLayout.vue'

// ---- 管理员端页面（复用现有 + 新建占位） ----
import Dashboard from '@/views/dashboard/Dashboard.vue'
import DeviceList from '@/views/devices/DeviceList.vue'
import KnowledgeList from '@/views/knowledge/KnowledgeList.vue'
import FaultReports from '@/views/faults/FaultReports.vue'
import RepairAdvice from '@/views/qa/RepairAdvice.vue'
import InspectionTemplateList from '@/views/inspections/InspectionTemplateList.vue'
import InspectionOrderList from '@/views/inspections/InspectionOrderList.vue'
import MaintenanceRecords from '@/views/maintenance/MaintenanceRecords.vue'
import MaintenanceAuditDetail from '@/views/maintenance/MaintenanceAuditDetail.vue'
import RepairCases from '@/views/cases/RepairCases.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import RoleConfig from '@/views/admin/RoleConfig.vue'
import KnowledgeGraph from '@/views/admin/KnowledgeGraph.vue'
import AuditLog from '@/views/admin/AuditLog.vue'
import DataBackup from '@/views/admin/DataBackup.vue'
import DeviceForm from '@/views/devices/DeviceForm.vue'
import KnowledgeUpload from '@/views/knowledge/KnowledgeUpload.vue'
import KnowledgeDetail from '@/views/knowledge/KnowledgeDetail.vue'
import InspectionTemplateForm from '@/views/inspections/InspectionTemplateForm.vue'
import AdminStats from '@/views/admin/AdminStats.vue'

// ---- 工人端页面 ----
import WorkerDashboard from '@/views/worker/WorkerFlowDashboard.vue'
import WorkerProfile from '@/views/worker/WorkerProfile.vue'
import WorkerDeviceView from '@/views/worker/WorkerDeviceView.vue'
import WorkerKnowledgeSearch from '@/views/worker/WorkerKnowledgeSearch.vue'
import WorkerFaultReport from '@/views/worker/WorkerFaultReport.vue'
import WorkerRepairAdvice from '@/views/worker/WorkerRepairAdvice.vue'
import WorkerInspection from '@/views/worker/WorkerInspection.vue'
import WorkerMaintenance from '@/views/worker/WorkerMaintenance.vue'
import WorkerCaseReport from '@/views/worker/WorkerCaseReport.vue'
import WorkerStats from '@/views/worker/WorkerStats.vue'
import WorkerKnowledgeGraph from '@/views/worker/WorkerKnowledgeGraph.vue'
import WorkerOffline from '@/views/worker/WorkerOffline.vue'
import WorkerMessages from '@/views/worker/WorkerMessages.vue'
import WorkerQuickPhrases from '@/views/worker/WorkerQuickPhrases.vue'

const routes = [
  {
    path: '/',
    name: 'Entry',
    component: EntryPage,
    meta: { public: true }
  },

  // ---- 管理员端 ----
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { public: true, role: 'admin' }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: Dashboard, meta: { title: '系统概览' } },
      { path: 'users', name: 'UserManagement', component: UserManagement, meta: { title: '用户管理' } },
      { path: 'roles', name: 'RoleConfig', component: RoleConfig, meta: { title: '角色与权限配置' } },
      { path: 'devices', name: 'AdminDevices', component: DeviceList, meta: { title: '设备管理' } },
      { path: 'devices/add', name: 'DeviceAdd', component: DeviceForm, meta: { title: '添加设备' } },
      { path: 'devices/:id/edit', name: 'DeviceEdit', component: DeviceForm, meta: { title: '编辑设备' } },
      { path: 'knowledge', name: 'AdminKnowledge', component: KnowledgeList, meta: { title: '检修知识库管理' } },
      { path: 'knowledge/add', name: 'KnowledgeAdd', component: KnowledgeUpload, meta: { title: '上传知识文件' } },
      { path: 'knowledge/:id/edit', name: 'KnowledgeEdit', component: KnowledgeDetail, meta: { title: '知识文件详情' } },
      { path: 'cases', name: 'AdminCases', component: RepairCases, meta: { title: '故障案例审核入库' } },
      { path: 'knowledge-graph', name: 'KnowledgeGraph', component: KnowledgeGraph, meta: { title: '知识图谱可视化' } },
      { path: 'stats', name: 'AdminStats', component: AdminStats, meta: { title: '系统数据统计' } },
      { path: 'faults', name: 'AdminFaults', component: FaultReports, meta: { title: '多模态故障检索' } },
      { path: 'repair-advice', name: 'AdminRepairAdvice', component: RepairAdvice, meta: { title: '智能检修建议复核' } },
      { path: 'inspection-templates', name: 'InspectionTemplates', component: InspectionTemplateList, meta: { title: '点检工单模板管理' } },
      { path: 'inspection-templates/add', name: 'InspectionTemplateAdd', component: InspectionTemplateForm, meta: { title: '创建点检模板' } },
      { path: 'inspection-templates/edit/:id', name: 'InspectionTemplateEdit', component: InspectionTemplateForm, meta: { title: '编辑点检模板' } },
      { path: 'all-inspections', name: 'AllInspections', component: InspectionOrderList, meta: { title: '所有工单监控' } },
      { path: 'maintenance-audit', name: 'MaintenanceAudit', component: MaintenanceRecords, meta: { title: '维保记录审核' } },
      { path: 'maintenance-audit/:id', name: 'MaintenanceAuditDetail', component: MaintenanceAuditDetail, meta: { title: '审核详情' } },
      { path: 'audit-log', name: 'AuditLog', component: AuditLog, meta: { title: '操作日志审计' } },
      { path: 'data-backup', name: 'DataBackup', component: DataBackup, meta: { title: '数据备份与恢复' } }
    ]
  },

  // ---- 维修工人端 ----
  {
    path: '/worker/login',
    name: 'WorkerLogin',
    component: WorkerLogin,
    meta: { public: true, role: 'worker' }
  },
  {
    path: '/worker',
    component: WorkerLayout,
    meta: { requiresAuth: true, role: 'worker' },
    children: [
      { path: '', redirect: '/worker/dashboard' },
      { path: 'dashboard', name: 'WorkerDashboard', component: WorkerDashboard, meta: { title: '工作台' } },
      { path: 'profile', name: 'WorkerProfile', component: WorkerProfile, meta: { title: '个人信息维护' } },
      { path: 'devices', name: 'WorkerDevices', component: WorkerDeviceView, meta: { title: '设备信息查看' } },
      { path: 'knowledge', name: 'WorkerKnowledge', component: WorkerKnowledgeSearch, meta: { title: '知识库查询' } },
      { path: 'faults', name: 'WorkerFaults', component: WorkerFaultReport, meta: { title: '多模态故障检索' } },
      { path: 'repair-advice', name: 'WorkerRepairAdvice', component: WorkerRepairAdvice, meta: { title: '智能检修建议' } },
      { path: 'inspections', name: 'WorkerInspections', component: WorkerInspection, meta: { title: '点检工单执行' } },
      { path: 'maintenance', name: 'WorkerMaintenance', component: WorkerMaintenance, meta: { title: '维保记录与报告' } },
      { path: 'case-report', name: 'WorkerCaseReport', component: WorkerCaseReport, meta: { title: '故障案例上报' } },
      { path: 'stats', name: 'WorkerStats', component: WorkerStats, meta: { title: '个人工作统计' } },
      { path: 'knowledge-graph', name: 'WorkerKnowledgeGraph', component: WorkerKnowledgeGraph, meta: { title: '知识图谱查询' } },
      { path: 'offline', name: 'WorkerOffline', component: WorkerOffline, meta: { title: '离线工单缓存' } },
      { path: 'messages', name: 'WorkerMessages', component: WorkerMessages, meta: { title: '工单消息提醒' } },
      { path: 'quick-phrases', name: 'WorkerQuickPhrases', component: WorkerQuickPhrases, meta: { title: '快捷短语' } }
    ]
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ---- 全局路由守卫 ----
router.beforeEach((to, from, next) => {
  const token = getToken()
  const role = getRole()

  // 公开页面直接放行
  if (to.meta.public) {
    // 已登录用户访问登录页 → 重定向到对应首页
    if (token && (to.path === '/admin/login' || to.path === '/worker/login')) {
      if (role === 'admin') return next('/admin/dashboard')
      if (role === 'worker') return next('/worker/dashboard')
    }
    return next()
  }

  // 需要认证但未登录
  if (!token) {
    if (to.path.startsWith('/admin')) return next('/admin/login')
    if (to.path.startsWith('/worker')) return next('/worker/login')
    return next('/')
  }

  // 角色不匹配
  const routeRole = to.meta.role
  if (routeRole && role !== routeRole) {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    if (routeRole === 'admin') return next('/admin/login')
    if (routeRole === 'worker') return next('/worker/login')
    return next('/')
  }

  next()
})

export default router
