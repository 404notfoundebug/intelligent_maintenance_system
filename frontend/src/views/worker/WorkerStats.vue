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
        <el-card>
          <template #header><span>本月工单状态分布</span></template>
          <div ref="orderPieRef" style="height:300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>近6月工单趋势</span></template>
          <div ref="trendRef" style="height:300px"></div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="24">
        <el-card>
          <template #header><span>最近工单记录</span></template>
          <el-empty v-if="!recentOrders.length" description="暂无工单记录" :image-size="80" />
          <el-table v-else :data="recentOrders" size="small" max-height="320">
            <el-table-column prop="id" label="工单号" width="80" />
            <el-table-column prop="title" label="工单名称" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">{{ row.title || row.template_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="device_name" label="设备" min-width="120" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="110">
              <template #default="{ row }">{{ fmt(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import request from '@/api/request'
import * as echarts from 'echarts'

const loading = ref(false)
const orderPieRef = ref(null)
const trendRef = ref(null)
let orderPieChart = null
let trendChart = null

const stats = ref([
  { label: '完成工单数', value: 0, color: '#67c23a' },
  { label: '上报案例数', value: 0, color: '#409eff' },
  { label: '审核通过率', value: '--', color: '#e6a23c' },
  { label: '平均响应(h)', value: '--', color: '#909399' }
])

const recentOrders = ref([])

function fmt(s) { return s ? s.slice(0, 10) : '' }
function statusText(s) { return { pending: '待处理', in_progress: '进行中', completed: '已完成', cancelled: '已取消', assigned: '已分配', overdue: '已逾期' }[s] || s || '-' }
function statusTag(s) { return { pending: 'warning', in_progress: '', completed: 'success', cancelled: 'info', assigned: 'warning', overdue: 'danger' }[s] || 'info' }

function renderOrderPie(data) {
  if (!orderPieRef.value) return
  if (!orderPieChart) orderPieChart = echarts.init(orderPieRef.value)
  const pieData = []
  const map = {}
  ;(data || []).forEach(o => {
    const key = statusText(o.status)
    map[key] = (map[key] || 0) + 1
  })
  for (const [name, value] of Object.entries(map)) pieData.push({ name, value })
  orderPieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '70%'], data: pieData.length ? pieData : [{ name: '暂无数据', value: 1 }], label: { show: true, formatter: '{b}: {c}' } }]
  })
}

function renderTrend(data) {
  if (!trendRef.value) return
  if (!trendChart) trendChart = echarts.init(trendRef.value)
  const months = (data || []).map(d => d.month || d.label || '').slice(-6)
  const values = (data || []).map(d => d.count || d.value || 0).slice(-6)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: months.length ? months : ['暂无数据'] },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'line', data: values.length ? values : [0], smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: '#409eff' } }]
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const [summaryRes, ordersRes, casesRes, trendRes] = await Promise.all([
      request.get('/api/dashboard/summary'),
      request.get('/api/inspections/orders?limit=200'),
      request.get('/api/cases?limit=200'),
      request.get('/api/dashboard/monthly-trend')
    ])

    const s = summaryRes || {}
    const orders = ordersRes?.items || ordersRes || []
    const cases = casesRes?.items || casesRes || []

    const completed = orders.filter(o => o.status === 'completed').length
    const approvedCases = (Array.isArray(cases) ? cases : []).filter(c => c.status === 'approved' || c.audit_status === 'approved').length
    const totalCases = (Array.isArray(cases) ? cases : []).length

    stats.value = [
      { label: '完成工单数', value: completed, color: '#67c23a' },
      { label: '上报案例数', value: totalCases, color: '#409eff' },
      { label: '审核通过率', value: totalCases > 0 ? Math.round(approvedCases / totalCases * 100) + '%' : '--', color: '#e6a23c' },
      { label: '设备总数', value: s.device_count || 0, color: '#909399' }
    ]

    recentOrders.value = (Array.isArray(orders) ? orders : []).slice(0, 20)
    renderOrderPie(orders)
    renderTrend(trendRes || [])
  } catch {
    // 静默
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  orderPieChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.page-container { padding: 0; }
.stat-card { text-align: center; }
.stat-value { font-size: 2rem; font-weight: 700; }
.stat-label { color: #909399; margin-top: 8px; }
</style>
