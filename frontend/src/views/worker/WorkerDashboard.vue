<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" class="stat-card" v-loading="loading">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card v-loading="loading">
          <template #header><span>待办工单</span></template>
          <el-empty v-if="!todos.length" description="暂无待办工单" :image-size="80" />
          <el-timeline v-else>
            <el-timeline-item v-for="item in todos" :key="item.id" :timestamp="item.time" placement="top">
              <el-card shadow="hover">
                <p><strong>{{ item.title }}</strong></p>
                <p style="color:#909399;font-size:13px;margin-top:4px">
                  {{ item.device_name || '' }} &nbsp; 
                  <el-tag size="small" :type="item.status === 'pending' ? 'warning' : 'info'">{{ item.status_text || '待处理' }}</el-tag>
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card v-loading="loading">
          <template #header><span>最近维保记录</span></template>
          <el-empty v-if="!recentRecords.length" description="暂无维保记录" :image-size="80" />
          <el-table v-else :data="recentRecords" size="small" max-height="300">
            <el-table-column prop="device_name" label="设备" min-width="100" />
            <el-table-column prop="content" label="维保内容" min-width="120" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="100">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="24">
        <el-card>
          <template #header><span>快捷入口</span></template>
          <el-row :gutter="12">
            <el-col :span="4" v-for="action in quickActions" :key="action.label">
              <el-button :type="action.type" style="width:100%;height:80px;margin-bottom:12px" @click="$router.push(action.path)">
                <div>
                  <el-icon :size="24"><component :is="action.icon" /></el-icon>
                  <div style="margin-top:4px">{{ action.label }}</div>
                </div>
              </el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, ChatLineRound, Checked, Warning, Document } from '@element-plus/icons-vue'
import request from '@/api/request'

const loading = ref(false)

const stats = ref([
  { label: '待处理工单', value: 0, color: '#e6a23c' },
  { label: '本月完成', value: 0, color: '#67c23a' },
  { label: '上报案例', value: 0, color: '#409eff' },
  { label: '完成率', value: '--', color: '#67c23a' }
])

const todos = ref([])
const recentRecords = ref([])

const quickActions = [
  { label: '故障检索', icon: Search, type: 'primary', path: '/worker/faults' },
  { label: '检修建议', icon: ChatLineRound, type: 'success', path: '/worker/repair-advice' },
  { label: '执行工单', icon: Checked, type: 'warning', path: '/worker/inspections' },
  { label: '上报案例', icon: Warning, type: 'danger', path: '/worker/case-report' },
  { label: '维保记录', icon: Document, type: 'info', path: '/worker/maintenance' },
  { label: '知识库', icon: Search, type: '', path: '/worker/knowledge' }
]

function formatDate(str) {
  if (!str) return ''
  return str.slice(0, 10)
}

function getStatusText(status) {
  const map = { pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }
  return map[status] || status || '待处理'
}

onMounted(async () => {
  loading.value = true
  try {
    const [summaryRes, ordersRes, recordsRes, casesRes] = await Promise.all([
      request.get('/api/dashboard/summary'),
      request.get('/api/inspections/orders?limit=5'),
      request.get('/api/dashboard/recent-maintenance-records'),
      request.get('/api/cases?limit=100')
    ])

    const s = summaryRes || {}
    const orders = ordersRes?.items || ordersRes || []
    const records = recordsRes || []
    const cases = casesRes?.items || casesRes || []

    // 统计卡片
    const pendingOrders = orders.filter(o => o.status === 'pending' || o.status === 'assigned').length
    const completedThisMonth = s.inspection_order_count || orders.filter(o => o.status === 'completed').length
    stats.value = [
      { label: '待处理工单', value: pendingOrders, color: '#e6a23c' },
      { label: '本月完成', value: completedThisMonth, color: '#67c23a' },
      { label: '上报案例', value: Array.isArray(cases) ? cases.length : (s.case_count || 0), color: '#409eff' },
      { label: '完成率', value: completedThisMonth > 0 ? Math.round(completedThisMonth / (completedThisMonth + pendingOrders) * 100) + '%' : '--', color: '#67c23a' }
    ]

    // 待办工单
    todos.value = orders
      .filter(o => o.status !== 'completed' && o.status !== 'cancelled')
      .slice(0, 5)
      .map(o => ({
        id: o.id,
        title: o.title || o.template_name || `工单 #${o.id}`,
        device_name: o.device_name || '',
        time: o.created_at ? o.created_at.slice(0, 10) : '',
        status: o.status,
        status_text: getStatusText(o.status)
      }))

    // 最近维保记录
    recentRecords.value = (Array.isArray(records) ? records : []).slice(0, 8)
  } catch {
    // 静默失败，保留默认值
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container { padding: 0; }
.stat-card { text-align: center; cursor: pointer; }
.stat-value { font-size: 2rem; font-weight: 700; }
.stat-label { color: #909399; margin-top: 8px; }
</style>
