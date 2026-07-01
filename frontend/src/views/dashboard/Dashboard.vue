<template>
  <div class="admin-dashboard-page">
    <section class="dashboard-hero">
      <div>
        <span class="hero-kicker">管理控制台</span>
        <h1>系统运营总览</h1>
        <p>欢迎回来，{{ userName }}。这里聚合设备、工单、知识库和审核事项，方便快速进入各个管理模块。</p>
      </div>
      <el-button class="refresh-button" type="primary" :loading="loading" @click="loadDashboard">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </section>

    <el-alert
      v-if="errorText"
      class="dashboard-alert"
      type="error"
      :title="errorText"
      show-icon
      :closable="false"
    />

    <section class="metric-grid">
      <article v-for="item in metrics" :key="item.label" class="metric-card">
        <div class="metric-icon" :class="item.tone">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div class="metric-copy">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </article>
    </section>

    <section class="dashboard-grid">
      <div class="panel module-panel">
        <div class="panel-heading">
          <div>
            <span class="panel-kicker">快捷入口</span>
            <h2>核心管理模块</h2>
          </div>
          <el-tag type="primary" effect="light">Admin</el-tag>
        </div>
        <div class="module-grid">
          <button v-for="item in moduleLinks" :key="item.path" class="module-card" @click="router.push(item.path)">
            <span class="module-icon" :class="item.tone">
              <el-icon><component :is="item.icon" /></el-icon>
            </span>
            <span class="module-title">{{ item.title }}</span>
            <span class="module-desc">{{ item.desc }}</span>
          </button>
        </div>
      </div>

      <div class="panel attention-panel">
        <div class="panel-heading">
          <div>
            <span class="panel-kicker">待处理</span>
            <h2>需要关注</h2>
          </div>
        </div>
        <div class="attention-list">
          <button v-for="item in attentionItems" :key="item.label" class="attention-item" @click="router.push(item.path)">
            <span class="attention-dot" :class="item.tone"></span>
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </button>
        </div>
      </div>
    </section>

    <section class="dashboard-grid secondary-grid">
      <div class="panel status-panel">
        <div class="panel-heading">
          <div>
            <span class="panel-kicker">资源状态</span>
            <h2>设备运行分布</h2>
          </div>
        </div>
        <div class="status-bars">
          <div v-for="item in deviceStatus" :key="item.label" class="status-row">
            <div class="status-row-top">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :class="item.tone" :style="{ width: item.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel recent-panel">
        <div class="panel-heading">
          <div>
            <span class="panel-kicker">近期动态</span>
            <h2>最新工单与故障</h2>
          </div>
        </div>
        <div class="recent-list">
          <div v-if="recentItems.length === 0" class="empty-state">暂无近期动态</div>
          <button v-for="item in recentItems" :key="item.key" class="recent-item" @click="router.push(item.path)">
            <span class="recent-type" :class="item.tone">{{ item.type }}</span>
            <span class="recent-title">{{ item.title }}</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getDashboardSummary, getRecentFaults, getRecentOrders } from '../../api/dashboard'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const errorText = ref('')
const summary = ref({})
const recentFaults = ref([])
const recentOrders = ref([])

const userName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '管理员')

const metrics = computed(() => [
  { label: '设备总数', value: summary.value.device_count || 0, icon: 'Cpu', tone: 'blue' },
  { label: '故障上报', value: summary.value.fault_report_count || 0, icon: 'Warning', tone: 'red' },
  { label: '点检工单', value: summary.value.inspection_order_count || 0, icon: 'Checked', tone: 'cyan' },
  { label: '知识库文档', value: summary.value.knowledge_file_count || 0, icon: 'Collection', tone: 'violet' }
])

const moduleLinks = [
  { title: '设备管理', desc: '维护设备台账和状态', path: '/admin/devices', icon: 'Cpu', tone: 'blue' },
  { title: '工单监控', desc: '查看全部点检工单', path: '/admin/all-inspections', icon: 'List', tone: 'cyan' },
  { title: '知识库管理', desc: '上传和维护检修资料', path: '/admin/knowledge', icon: 'Collection', tone: 'violet' },
  { title: '案例审核', desc: '审核故障案例入库', path: '/admin/cases', icon: 'Notebook', tone: 'amber' },
  { title: '用户管理', desc: '维护账号和角色权限', path: '/admin/users', icon: 'User', tone: 'blue' },
  { title: '数据统计', desc: '查看系统指标趋势', path: '/admin/stats', icon: 'TrendCharts', tone: 'green' }
]

const attentionItems = computed(() => [
  { label: '待处理故障', value: summary.value.pending_fault_count || 0, path: '/admin/faults', tone: 'red' },
  { label: '待审核案例', value: summary.value.pending_case_count || 0, path: '/admin/cases', tone: 'amber' },
  { label: '维保中设备', value: summary.value.maintenance_device_count || 0, path: '/admin/devices', tone: 'blue' },
  { label: '已完成工单', value: summary.value.completed_order_count || 0, path: '/admin/all-inspections', tone: 'green' }
])

const deviceStatus = computed(() => {
  const normal = summary.value.normal_device_count || 0
  const fault = summary.value.fault_device_count || 0
  const maintenance = summary.value.maintenance_device_count || 0
  const total = Math.max(normal + fault + maintenance, 1)

  return [
    { label: '正常设备', value: normal, percent: Math.round((normal / total) * 100), tone: 'green' },
    { label: '故障设备', value: fault, percent: Math.round((fault / total) * 100), tone: 'red' },
    { label: '维保中设备', value: maintenance, percent: Math.round((maintenance / total) * 100), tone: 'blue' }
  ]
})

const recentItems = computed(() => {
  const faults = recentFaults.value.slice(0, 3).map((item, index) => ({
    key: `fault-${item.id || index}`,
    type: '故障',
    title: item.title || item.description || item.fault_type || `故障记录 ${index + 1}`,
    path: '/admin/faults',
    tone: 'red'
  }))

  const orders = recentOrders.value.slice(0, 3).map((item, index) => ({
    key: `order-${item.id || index}`,
    type: '工单',
    title: item.title || item.order_no || item.name || `点检工单 ${index + 1}`,
    path: '/admin/all-inspections',
    tone: 'blue'
  }))

  return [...faults, ...orders].slice(0, 5)
})

async function loadDashboard() {
  loading.value = true
  errorText.value = ''
  try {
    const [summaryResult, faultsResult, ordersResult] = await Promise.allSettled([
      getDashboardSummary(),
      getRecentFaults({ limit: 5 }),
      getRecentOrders({ limit: 5 })
    ])

    if (summaryResult.status === 'fulfilled') {
      summary.value = summaryResult.value
    } else {
      throw summaryResult.reason
    }

    recentFaults.value = faultsResult.status === 'fulfilled' ? normalizeList(faultsResult.value) : []
    recentOrders.value = ordersResult.status === 'fulfilled' ? normalizeList(ordersResult.value) : []
  } catch (error) {
    errorText.value = 'Dashboard 数据加载失败，请确认后端服务和登录状态正常。'
    ElMessage.error(errorText.value)
  } finally {
    loading.value = false
  }
}

function normalizeList(value) {
  if (Array.isArray(value)) return value
  if (Array.isArray(value?.items)) return value.items
  if (Array.isArray(value?.data)) return value.data
  return []
}

onMounted(loadDashboard)
</script>

<style scoped>
.admin-dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dashboard-hero {
  min-height: 166px;
  padding: 26px 28px;
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(29, 78, 216, 0.96), rgba(14, 165, 233, 0.9)),
    radial-gradient(circle at 92% 18%, rgba(255, 255, 255, 0.28), transparent 24%);
  color: #FFFFFF;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  box-shadow: 0 22px 50px rgba(37, 99, 235, 0.22);
}

.hero-kicker,
.panel-kicker {
  display: inline-flex;
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
}

.dashboard-hero h1 {
  margin: 10px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.dashboard-hero p {
  max-width: 680px;
  margin: 0;
  color: rgba(239, 246, 255, 0.9);
  font-size: 14px;
  line-height: 1.7;
}

.refresh-button {
  flex-shrink: 0;
  border-color: rgba(255, 255, 255, 0.44);
  background: rgba(255, 255, 255, 0.18);
}

.dashboard-alert {
  border-radius: 8px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  min-height: 106px;
  padding: 18px;
  border: 1px solid rgba(191, 219, 254, 0.75);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  display: flex;
  align-items: center;
  gap: 14px;
}

.metric-icon,
.module-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  flex-shrink: 0;
}

.metric-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.metric-copy span {
  color: #64748B;
  font-size: 13px;
}

.metric-copy strong {
  color: #0F172A;
  font-size: 26px;
  line-height: 1;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.85fr);
  gap: 18px;
}

.secondary-grid {
  grid-template-columns: minmax(320px, 0.92fr) minmax(0, 1.18fr);
}

.panel {
  border: 1px solid rgba(191, 219, 254, 0.72);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
  padding: 18px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-kicker {
  color: #2563EB;
}

.panel h2 {
  margin: 6px 0 0;
  color: #0F172A;
  font-size: 18px;
  letter-spacing: 0;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.module-card,
.attention-item,
.recent-item {
  border: none;
  font: inherit;
  cursor: pointer;
  text-align: left;
}

.module-card {
  min-height: 126px;
  padding: 16px;
  border-radius: 8px;
  background: #F8FBFF;
  border: 1px solid rgba(219, 234, 254, 0.95);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.5);
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.12);
}

.module-title {
  color: #0F172A;
  font-weight: 700;
  font-size: 15px;
}

.module-desc {
  color: #64748B;
  font-size: 12px;
  line-height: 1.5;
}

.attention-list,
.recent-list,
.status-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attention-item {
  height: 52px;
  padding: 0 14px;
  border-radius: 8px;
  background: #F8FBFF;
  border: 1px solid rgba(219, 234, 254, 0.95);
  display: grid;
  grid-template-columns: 12px 1fr auto;
  align-items: center;
  gap: 10px;
  color: #334155;
}

.attention-item strong {
  color: #0F172A;
  font-size: 18px;
}

.attention-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
}

.status-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-row-top {
  display: flex;
  justify-content: space-between;
  color: #475569;
  font-size: 13px;
}

.bar-track {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: #E2E8F0;
}

.bar-fill {
  height: 100%;
  min-width: 4px;
  border-radius: 999px;
}

.recent-item {
  min-height: 46px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #F8FBFF;
  border: 1px solid rgba(219, 234, 254, 0.95);
  display: grid;
  grid-template-columns: 44px 1fr;
  align-items: center;
  gap: 10px;
}

.recent-type {
  justify-self: start;
  padding: 3px 8px;
  border-radius: 999px;
  color: #FFFFFF;
  font-size: 12px;
}

.recent-title {
  min-width: 0;
  color: #334155;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-state {
  height: 126px;
  border-radius: 8px;
  background: #F8FBFF;
  border: 1px dashed rgba(148, 163, 184, 0.55);
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue {
  background: linear-gradient(135deg, #2563EB, #38BDF8);
}

.cyan {
  background: linear-gradient(135deg, #0284C7, #22D3EE);
}

.violet {
  background: linear-gradient(135deg, #4F46E5, #8B5CF6);
}

.green {
  background: linear-gradient(135deg, #059669, #34D399);
}

.red {
  background: linear-gradient(135deg, #DC2626, #FB7185);
}

.amber {
  background: linear-gradient(135deg, #D97706, #FBBF24);
}

@media (max-width: 1180px) {
  .metric-grid,
  .module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-grid,
  .secondary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .dashboard-hero {
    flex-direction: column;
  }

  .metric-grid,
  .module-grid {
    grid-template-columns: 1fr;
  }
}
</style>
