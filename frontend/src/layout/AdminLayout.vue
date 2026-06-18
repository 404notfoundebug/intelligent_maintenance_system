<template>
  <el-container class="admin-layout">
    <el-aside width="240px" class="layout-sidebar">
      <div class="brand" @click="$router.push('/admin/dashboard')">
        <div class="brand-mark">IM</div>
        <div>
          <div class="brand-title">维保辅助系统</div>
          <div class="brand-subtitle">Maintenance AI · 管理端</div>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        router
        class="side-menu"
        background-color="#0f1b2d"
        text-color="#b8c5d8"
        active-text-color="#ffffff"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <span class="header-badge">管理员端</span>
          <span class="header-title">{{ currentPageTitle }}</span>
        </div>
        <div class="header-user">
          <el-tag type="primary" effect="light">管理员</el-tag>
          <span class="user-name">{{ userName }}</span>
          <el-button type="primary" plain size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

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

const userName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '管理员')
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
</style>
