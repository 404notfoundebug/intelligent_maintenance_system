<template>
  <el-container class="app-shell admin-shell">
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
      <button class="shell-brand" type="button" aria-label="返回管理员首页" @click="goHome">
        <span class="shell-brand-mark">
          <el-icon><Management /></el-icon>
        </span>
        <span class="shell-brand-copy">
          <span class="shell-brand-title">智能维保系统</span>
          <span class="shell-brand-subtitle">Operations Console</span>
        </span>
      </button>

      <div class="shell-nav-caption">管理导航</div>
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
          <small>系统管理员</small>
        </span>
        <el-button class="shell-logout" circle aria-label="退出管理员端" title="退出登录" @click="handleLogout">
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
            <p>设备、工单与知识决策中心</p>
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
import { Expand, Fold, Management, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarCollapsed = ref(false)
const mobileNavOpen = ref(false)
const isMobile = ref(false)

const menuItems = [
  { path: '/admin/dashboard', title: '系统概览', icon: 'DataBoard' },
  { path: '/admin/users', title: '用户管理', icon: 'User' },
  { path: '/admin/roles', title: '角色与权限', icon: 'Lock' },
  { path: '/admin/devices', title: '设备管理', icon: 'Cpu' },
  { path: '/admin/knowledge', title: '检修知识库', icon: 'Collection' },
  { path: '/admin/cases', title: '故障案例审核', icon: 'Notebook' },
  { path: '/admin/knowledge-graph', title: '知识图谱', icon: 'Share' },
  { path: '/admin/stats', title: '数据统计', icon: 'TrendCharts' },
  { path: '/admin/faults', title: '故障检索', icon: 'Search' },
  { path: '/admin/repair-advice', title: '检修建议复核', icon: 'ChatLineRound' },
  { path: '/admin/inspection-templates', title: '点检模板', icon: 'Checked' },
  { path: '/admin/all-inspections', title: '工单监控', icon: 'List' },
  { path: '/admin/maintenance-audit', title: '维保记录审核', icon: 'DocumentChecked' },
  { path: '/admin/audit-log', title: '操作日志', icon: 'Clock' },
  { path: '/admin/data-backup', title: '数据备份', icon: 'FolderOpened' }
]

function cleanDisplayName(value) {
  if (!value || /^[?\s]+$/.test(value)) return ''
  return value
}

const userName = computed(
  () => cleanDisplayName(userStore.userInfo?.real_name) || userStore.userInfo?.username || '管理员'
)
const userInitial = computed(() => userName.value.trim().slice(0, 1).toUpperCase())
const currentPageTitle = computed(() => route.meta?.title || '管理员端')
const sidebarWidth = computed(() => (isMobile.value ? '272px' : sidebarCollapsed.value ? '80px' : '260px'))
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
  router.push('/admin/dashboard')
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
