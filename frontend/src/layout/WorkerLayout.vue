<template>
  <el-container class="worker-layout">
    <el-aside width="220px" class="layout-sidebar">
      <div class="brand" @click="$router.push('/worker/dashboard')">
        <div class="brand-mark">IM</div>
        <div>
          <div class="brand-title">维保辅助系统</div>
          <div class="brand-subtitle">Maintenance AI · 工人端</div>
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
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <span class="header-badge worker">维修工人端</span>
          <span class="header-title">{{ currentPageTitle }}</span>
        </div>
        <div class="header-user">
          <el-tag type="success" effect="light">维修工人</el-tag>
          <span class="user-name">{{ userName }}</span>
          <el-button type="success" plain size="small" @click="handleLogout">退出登录</el-button>
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
  { path: '/worker/dashboard', title: '工作台', icon: 'DataBoard' },
  { path: '/worker/profile', title: '个人信息维护', icon: 'User' },
  { path: '/worker/devices', title: '设备信息查看', icon: 'Cpu' },
  { path: '/worker/knowledge', title: '知识库查询', icon: 'Collection' },
  { path: '/worker/faults', title: '多模态故障检索', icon: 'Search' },
  { path: '/worker/repair-advice', title: '智能检修建议', icon: 'ChatLineRound' },
  { path: '/worker/inspections', title: '点检工单执行', icon: 'Checked' },
  { path: '/worker/maintenance', title: '维保记录与报告', icon: 'DocumentChecked' },
  { path: '/worker/case-report', title: '故障案例上报', icon: 'Warning' },
  { path: '/worker/stats', title: '个人工作统计', icon: 'TrendCharts' },
  { path: '/worker/knowledge-graph', title: '知识图谱查询', icon: 'Share' },
  { path: '/worker/offline', title: '离线工单缓存', icon: 'FolderOpened' },
  { path: '/worker/messages', title: '工单消息提醒', icon: 'Bell' },
  { path: '/worker/quick-phrases', title: '快捷短语', icon: 'Edit' }
]

const userName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '维修工人')
const currentPageTitle = computed(() => route.meta?.title || '')

function handleLogout() {
  userStore.logout()
  router.replace('/')
}
</script>

<style scoped>
.worker-layout {
  height: 100vh;
}

.layout-sidebar {
  background-color: #1b4332;
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
  background: linear-gradient(135deg, #52b788, #40916c);
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
  color: #e0ede6;
  font-weight: 600;
  font-size: 15px;
}

.brand-subtitle {
  color: #88aa99;
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

.header-badge.worker {
  background: #67c23a;
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
