<template>
  <el-container class="worker-layout">
    <el-aside
      :width="sidebarExpanded ? '220px' : '60px'"
      class="layout-sidebar"
      :class="{ collapsed: !sidebarExpanded }"
      @mouseenter="sidebarExpanded = true"
      @mouseleave="sidebarExpanded = false"
    >
      <div class="brand" @click="$router.push('/worker/dashboard')">
        <div class="brand-mark"></div>
        <div class="brand-copy">
          <div class="brand-title">梯小维</div>
          <div class="brand-subtitle">现场维保工作台</div>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        router
        class="side-menu"
        background-color="#1b4332"
        text-color="#b8d8c5"
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
          <el-tag type="success" effect="light">维修工人</el-tag>
          <span class="sidebar-user-name">{{ userName }}</span>
        </div>
        <el-button
          class="sidebar-logout"
          type="success"
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
          <span class="header-badge worker">维修工人端</span>
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
  { path: '/worker/dashboard', title: '今日流程', icon: 'DataBoard' },
  { path: '/worker/inspections', title: '执行工单', icon: 'Checked' },
  { path: '/worker/faults', title: '故障检索', icon: 'Search' },
  { path: '/worker/repair-advice', title: '检修建议', icon: 'ChatLineRound' },
  { path: '/worker/maintenance', title: '维保记录', icon: 'DocumentChecked' },
  { path: '/worker/case-report', title: '案例上报', icon: 'Warning' },
  { path: '/worker/profile', title: '个人信息', icon: 'User' }
]

function cleanDisplayName(value) {
  if (!value || /^[?\s]+$/.test(value)) return ''
  return value
}

const userName = computed(() => cleanDisplayName(userStore.userInfo?.real_name) || userStore.userInfo?.username || '维修工人')
const currentPageTitle = computed(() => route.meta?.title || '')

function handleLogout() {
  userStore.logout()
  router.replace('/')
}
</script>

<style scoped>
.worker-layout {
  height: 100vh;
  background:
    radial-gradient(circle at 8% 8%, rgba(56, 189, 248, 0.12), transparent 30%),
    radial-gradient(circle at 92% 88%, rgba(167, 139, 250, 0.13), transparent 34%),
    linear-gradient(155deg, #F8FAFC 0%, #E0F2FE 48%, #F3E8FF 100%);
}

.worker-layout :deep(.el-container) {
  min-width: 0;
}

.layout-sidebar {
  background:
    linear-gradient(180deg, rgba(15, 35, 48, 0.94) 0%, rgba(18, 58, 49, 0.94) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: 18px 0 48px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
  transition: width 0.42s cubic-bezier(0.22, 1, 0.36, 1);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 86px;
  padding: 22px 18px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
  overflow: hidden;
}

.brand-mark {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #2563EB 0%, #38BDF8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.24);
}

.brand-mark::before,
.brand-mark::after {
  content: '';
  position: absolute;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
}

.brand-mark::before {
  left: 12px;
}

.brand-mark::after {
  right: 12px;
}

.brand-title {
  color: #F8FAFC;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.brand-subtitle {
  color: rgba(226, 232, 240, 0.72);
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
  border-right: none;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: 0;
  padding: 14px 10px;
  background: transparent !important;
}

.side-menu :deep(.el-menu-item) {
  height: 44px;
  margin: 4px 0;
  border-radius: 12px;
  padding: 0 16px !important;
  color: rgba(226, 232, 240, 0.78);
  font-size: 14px;
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
  padding-left: 8px;
  padding-right: 8px;
  align-items: center;
}

.layout-sidebar.collapsed .side-menu :deep(.el-menu-item) {
  width: 40px;
  min-width: 40px;
  height: 40px;
  margin: 4px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 !important;
  line-height: 40px;
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

.sidebar-user {
  margin-top: auto;
  padding: 14px 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
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
  color: rgba(226, 232, 240, 0.9);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-logout {
  width: 100%;
  justify-content: center;
  border-color: rgba(16, 185, 129, 0.36);
  background: rgba(16, 185, 129, 0.1);
  color: #D1FAE5;
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

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #FFFFFF !important;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.92), rgba(16, 185, 129, 0.82)) !important;
  color: #FFFFFF !important;
  box-shadow: 0 10px 22px rgba(16, 185, 129, 0.18);
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.7);
  padding: 0 26px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-badge {
  background: #2563EB;
  color: #fff;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 12px;
}

.header-badge.worker {
  background: linear-gradient(135deg, #2563EB, #10B981);
}

.header-title {
  color: #334155;
  font-size: 15px;
  font-weight: 600;
}

.layout-main {
  background:
    radial-gradient(circle at 100% 0%, rgba(56, 189, 248, 0.08), transparent 28%),
    radial-gradient(circle at 0% 100%, rgba(167, 139, 250, 0.08), transparent 30%),
    #F8FAFC;
  min-height: calc(100vh - 56px);
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}
</style>
