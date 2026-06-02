<template>
  <el-container class="admin-layout">
    <el-aside width="240px" class="layout-sidebar">
      <div class="brand">
        <div class="brand-mark">IM</div>
        <div>
          <div class="brand-title">维保辅助系统</div>
          <div class="brand-subtitle">Maintenance AI</div>
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
        <div class="header-title">面向电梯扶梯维保场景的多模态知识检索与标准化作业辅助系统</div>
        <div class="header-user">
          <el-tag type="primary" effect="light">{{ userRole }}</el-tag>
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
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { path: '/dashboard', title: '首页看板', icon: 'DataBoard' },
  { path: '/devices', title: '设备管理', icon: 'Cpu' },
  { path: '/knowledge', title: '知识库管理', icon: 'Collection' },
  { path: '/qa', title: '智能检修建议', icon: 'ChatLineRound' },
  { path: '/inspections', title: '点检工单', icon: 'Checked' },
  { path: '/maintenance', title: '维保记录', icon: 'DocumentChecked' },
  { path: '/faults', title: '故障上报', icon: 'Warning' },
  { path: '/cases', title: '检修案例', icon: 'Notebook' },
  { path: '/users', title: '用户管理', icon: 'User' }
]

const userName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '当前用户')
const userRole = computed(() => userStore.userInfo?.role || 'user')

function handleLogout() {
  userStore.logout()
  router.replace('/login')
}
</script>
