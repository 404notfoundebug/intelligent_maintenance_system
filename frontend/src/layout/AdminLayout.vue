<template>
  <el-container class="admin-layout">
    <el-aside
      :width="sidebarExpanded ? '236px' : '64px'"
      class="layout-sidebar"
      :class="{ collapsed: !sidebarExpanded }"
      @mouseenter="sidebarExpanded = true"
      @mouseleave="sidebarExpanded = false"
    >
      <div class="brand" @click="$router.push('/admin/dashboard')">
        <div class="brand-mark">
          <el-icon>
            <component is="Management" />
          </el-icon>
        </div>
        <div class="brand-copy">
          <div class="brand-title">智能维保系统</div>
          <div class="brand-subtitle">管理驾驶舱</div>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        router
        class="side-menu"
        background-color="#0B1F3A"
        text-color="#BFD7FF"
        active-text-color="#ffffff"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span class="menu-text">{{ item.title }}</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-user">
        <div class="sidebar-user-details">
          <el-tag type="primary" effect="light">管理员</el-tag>
          <span class="sidebar-user-name">{{ userName }}</span>
        </div>
        <el-button
          class="sidebar-logout"
          type="primary"
          plain
          size="small"
          :circle="!sidebarExpanded"
          @click="handleLogout"
        >
          <el-icon class="sidebar-logout-icon">
            <component is="SwitchButton" />
          </el-icon>
          <span class="logout-text">退出登录</span>
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <span class="header-badge">管理员端</span>
          <span class="header-title">{{ currentPageTitle }}</span>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarExpanded = ref(false)

const menuItems = [
  { path: '/admin/dashboard', title: '系统概览', icon: 'DataBoard' },
  { path: '/admin/users', title: '用户管理', icon: 'User' },
  { path: '/admin/roles', title: '角色与权限配置', icon: 'Lock' },
  { path: '/admin/devices', title: '设备管理', icon: 'Cpu' },
  { path: '/admin/knowledge', title: '检修知识库管理', icon: 'Collection' },
  { path: '/admin/cases', title: '故障案例审核入库', icon: 'Notebook' },
  { path: '/admin/knowledge-graph', title: '知识图谱可视化', icon: 'Share' },
  { path: '/admin/stats', title: '系统数据统计', icon: 'TrendCharts' },
  { path: '/admin/faults', title: '多模态故障检索', icon: 'Search' },
  { path: '/admin/repair-advice', title: '智能检修建议复核', icon: 'ChatLineRound' },
  { path: '/admin/inspection-templates', title: '点检工单模板管理', icon: 'Checked' },
  { path: '/admin/all-inspections', title: '所有工单监控', icon: 'List' },
  { path: '/admin/maintenance-audit', title: '维保记录审核', icon: 'DocumentChecked' },
  { path: '/admin/audit-log', title: '操作日志审计', icon: 'Clock' },
  { path: '/admin/data-backup', title: '数据备份与恢复', icon: 'FolderOpened' }
]

function cleanDisplayName(value) {
  if (!value || /^[?\s]+$/.test(value)) return ''
  return value
}

const userName = computed(() => cleanDisplayName(userStore.userInfo?.real_name) || userStore.userInfo?.username || '管理员')
const currentPageTitle = computed(() => route.meta?.title || '')

function handleLogout() {
  userStore.logout()
  router.replace('/')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.layout-sidebar {
  background-color: #0f1b2d;
  overflow-y: auto;
  overflow-x: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.brand-mark {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.brand-title {
  color: #e0e6ed;
  font-weight: 600;
  font-size: 15px;
}

.brand-subtitle {
  color: #8899aa;
  font-size: 11px;
}

.side-menu {
  border-right: none;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-badge {
  background: #409eff;
  color: #fff;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.header-title {
  color: #606266;
  font-size: 14px;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  color: #303133;
  font-size: 14px;
}

.layout-main {
  background: #f0f2f5;
  min-height: calc(100vh - 56px);
  padding: 20px;
}

.admin-layout {
  background:
    radial-gradient(circle at 10% 8%, rgba(59, 130, 246, 0.14), transparent 30%),
    radial-gradient(circle at 92% 88%, rgba(14, 165, 233, 0.12), transparent 34%),
    linear-gradient(155deg, #F8FAFC 0%, #EAF3FF 48%, #F7FBFF 100%);
}

.admin-layout :deep(.el-container) {
  min-width: 0;
}

.layout-sidebar {
  background:
    linear-gradient(180deg, rgba(8, 30, 59, 0.96) 0%, rgba(12, 55, 105, 0.95) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 18px 0 48px rgba(15, 23, 42, 0.14);
  display: flex;
  flex-direction: column;
  transition: width 0.42s cubic-bezier(0.22, 1, 0.36, 1);
}

.brand {
  min-height: 86px;
  padding: 22px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  overflow: hidden;
}

.brand-mark {
  border-radius: 14px;
  background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%);
  font-weight: 800;
  font-size: 13px;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.3);
}

.brand-mark .el-icon {
  font-size: 20px;
}

.brand-title {
  color: #F8FAFC;
  font-weight: 800;
  font-size: 17px;
  white-space: nowrap;
}

.brand-subtitle {
  color: rgba(219, 234, 254, 0.72);
  font-size: 12px;
  margin-top: 3px;
  white-space: nowrap;
}

.brand-copy {
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.28s ease, transform 0.34s ease, width 0.34s ease;
}

.side-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: 0;
  padding: 14px 10px;
  background: transparent !important;
}

.side-menu :deep(.el-menu-item) {
  height: 42px;
  margin: 3px 0;
  border-radius: 12px;
  padding: 0 14px !important;
  color: rgba(219, 234, 254, 0.82);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0;
  flex-shrink: 0;
  overflow: hidden;
  transition:
    padding 0.34s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.side-menu :deep(.el-menu-item .el-icon) {
  width: 20px;
  margin-right: 10px;
  font-size: 16px;
  flex-shrink: 0;
  transition: margin 0.34s ease;
}

.menu-text {
  white-space: nowrap;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.26s ease, transform 0.34s ease, width 0.34s ease;
}

.layout-sidebar.collapsed .brand {
  gap: 0;
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}

.layout-sidebar.collapsed .brand-copy {
  opacity: 0;
  width: 0;
  transform: translateX(-8px);
  pointer-events: none;
}

.layout-sidebar.collapsed .side-menu {
  padding-left: 10px;
  padding-right: 10px;
  align-items: center;
}

.layout-sidebar.collapsed .side-menu :deep(.el-menu-item) {
  width: 42px;
  min-width: 42px;
  height: 42px;
  margin: 3px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 !important;
  line-height: 42px;
}

.layout-sidebar.collapsed .side-menu :deep(.el-menu-item .el-icon) {
  width: 20px;
  height: 20px;
  margin: 0 !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.layout-sidebar.collapsed .menu-text {
  display: none;
  opacity: 0;
  width: 0;
  transform: translateX(-8px);
  pointer-events: none;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.09) !important;
  color: #FFFFFF !important;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.95), rgba(14, 165, 233, 0.86)) !important;
  color: #FFFFFF !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.24);
}

.sidebar-user {
  margin-top: auto;
  padding: 14px 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-user-details {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.26s ease, transform 0.34s ease, height 0.34s ease;
}

.sidebar-user-name {
  min-width: 0;
  color: rgba(219, 234, 254, 0.92);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-logout {
  width: 100%;
  justify-content: center;
  border-radius: 14px;
  border-color: rgba(96, 165, 250, 0.42);
  background: rgba(37, 99, 235, 0.12);
  color: #DBEAFE;
}

.sidebar-logout-icon {
  margin-right: 6px;
}

.layout-sidebar.collapsed .sidebar-user {
  align-items: center;
  padding: 12px 0 14px;
}

.layout-sidebar.collapsed .sidebar-user-details {
  height: 0;
  opacity: 0;
  transform: translateX(-8px);
  pointer-events: none;
}

.layout-sidebar.collapsed .sidebar-logout {
  width: 40px;
  height: 40px;
  padding: 0;
}

.layout-sidebar.collapsed .sidebar-logout-icon {
  margin-right: 0;
}

.layout-sidebar.collapsed .logout-text {
  display: none;
}

.layout-header {
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(191, 219, 254, 0.78);
  padding: 0 26px;
  height: 64px;
}

.header-badge {
  background: linear-gradient(135deg, #2563EB, #0EA5E9);
  padding: 4px 11px;
  border-radius: 999px;
}

.header-title {
  color: #334155;
  font-size: 15px;
  font-weight: 600;
}

.layout-main {
  background:
    radial-gradient(circle at 100% 0%, rgba(59, 130, 246, 0.1), transparent 28%),
    radial-gradient(circle at 0% 100%, rgba(14, 165, 233, 0.08), transparent 30%),
    #F8FAFC;
  min-height: calc(100vh - 64px);
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}
</style>
