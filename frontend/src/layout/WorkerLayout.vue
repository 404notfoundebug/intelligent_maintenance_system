<template>
  <el-container class="app-shell worker-shell">
    <Transition name="shell-scrim">
      <button
        v-if="isMobile && mobileNavOpen"
        class="shell-mobile-scrim"
        type="button"
        aria-label="关闭导航"
        @click="mobileNavOpen = false"
      ></button>
    </Transition>

    <el-aside
      :width="sidebarWidth"
      class="shell-sidebar"
      :class="{
        'is-collapsed': sidebarCollapsed && !isMobile,
        'is-mobile': isMobile,
        'is-open': mobileNavOpen
      }"
    >
      <button class="shell-brand" type="button" aria-label="返回工人工作台" @click="goHome">
        <span class="shell-brand-mark">
          <el-icon><Tools /></el-icon>
        </span>
        <span class="shell-brand-copy">
          <span class="shell-brand-title">梯小维</span>
          <span class="shell-brand-subtitle">Field Service</span>
        </span>
      </button>

      <div class="shell-nav-caption">现场作业</div>
      <el-menu :default-active="route.path" router class="shell-menu">
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
          :title="sidebarCollapsed && !isMobile ? item.title : undefined"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span class="shell-menu-label">{{ item.title }}</span>
        </el-menu-item>
      </el-menu>

      <div class="shell-account">
        <span class="shell-avatar">{{ userInitial }}</span>
        <span class="shell-account-copy">
          <strong>{{ userName }}</strong>
          <small>现场维保人员</small>
        </span>
        <el-button class="shell-logout" circle aria-label="退出工人端" title="退出登录" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <el-container class="shell-content">
      <el-header class="shell-header">
        <div class="shell-header-left">
          <el-button class="shell-toggle" circle :aria-label="toggleLabel" :title="toggleLabel" @click="toggleNavigation">
            <el-icon><Fold v-if="!sidebarCollapsed && !isMobile" /><Expand v-else /></el-icon>
          </el-button>
          <div class="shell-page-copy">
            <h1>{{ currentPageTitle }}</h1>
            <p>专注今天最重要的现场任务</p>
          </div>
        </div>

        <div class="shell-header-right">
          <span class="shell-date-pill">{{ formattedDate }}</span>
          <span class="shell-user-pill">
            <i class="shell-user-dot"></i>
            <span>{{ userName }}</span>
          </span>
        </div>
      </el-header>

      <el-main class="shell-main">
        <router-view v-slot="{ Component }">
          <transition name="shell-route" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Expand, Fold, SwitchButton, Tools } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarCollapsed = ref(false)
const mobileNavOpen = ref(false)
const isMobile = ref(false)

const menuItems = [
  { path: '/worker/dashboard', title: '今日流程', icon: 'DataBoard' },
  { path: '/worker/inspections', title: '执行工单', icon: 'Checked' },
  { path: '/worker/devices', title: '设备信息', icon: 'Cpu' },
  { path: '/worker/knowledge', title: '知识库查询', icon: 'Collection' },
  { path: '/worker/faults', title: '故障检索', icon: 'Search' },
  { path: '/worker/repair-advice', title: '检修建议', icon: 'ChatLineRound' },
  { path: '/worker/maintenance', title: '维保记录', icon: 'DocumentChecked' },
  { path: '/worker/case-report', title: '案例上报', icon: 'Warning' },
  { path: '/worker/stats', title: '工作统计', icon: 'TrendCharts' },
  { path: '/worker/messages', title: '工单消息', icon: 'Bell' },
  { path: '/worker/profile', title: '个人信息', icon: 'User' }
]

function cleanDisplayName(value) {
  if (!value || /^[?\s]+$/.test(value)) return ''
  return value
}

const userName = computed(
  () => cleanDisplayName(userStore.userInfo?.real_name) || userStore.userInfo?.username || '维修工人'
)
const userInitial = computed(() => userName.value.trim().slice(0, 1).toUpperCase())
const currentPageTitle = computed(() => route.meta?.title || '工人端')
const sidebarWidth = computed(() => (isMobile.value ? '272px' : sidebarCollapsed.value ? '80px' : '250px'))
const toggleLabel = computed(() => {
  if (isMobile.value) return mobileNavOpen.value ? '关闭导航' : '打开导航'
  return sidebarCollapsed.value ? '展开导航' : '收起导航'
})
const formattedDate = new Intl.DateTimeFormat('zh-CN', {
  month: 'long',
  day: 'numeric',
  weekday: 'short'
}).format(new Date())

function updateViewport() {
  isMobile.value = window.innerWidth <= 900
  if (!isMobile.value) mobileNavOpen.value = false
}

function toggleNavigation() {
  if (isMobile.value) mobileNavOpen.value = !mobileNavOpen.value
  else sidebarCollapsed.value = !sidebarCollapsed.value
}

function goHome() {
  router.push('/worker/dashboard')
  mobileNavOpen.value = false
}

function handleLogout() {
  userStore.logout()
  router.replace('/')
}

watch(
  () => route.path,
  () => {
    if (isMobile.value) mobileNavOpen.value = false
  }
)

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport, { passive: true })
})

onBeforeUnmount(() => window.removeEventListener('resize', updateViewport))
</script>
