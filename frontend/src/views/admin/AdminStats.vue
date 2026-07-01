<template>
  <div class="admin-stats-page">
    <h2>系统数据统计</h2>

    <!-- 概览卡片 -->
    <el-row :gutter="16" class="summary-cards">
      <el-col :span="6" v-for="card in summaryCards" :key="card.label">
        <el-card shadow="hover" :body-style="{ padding: '20px' }">
          <div class="card-inner">
            <div class="card-icon" :style="{ background: card.bg }">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ card.value }}</div>
              <div class="card-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card>
          <template #header>设备状态分布</template>
          <div ref="deviceChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>故障报告状态</template>
          <div ref="faultChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card>
          <template #header>工单状态分布</template>
          <div ref="orderChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>近6个月趋势</template>
          <div ref="trendChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, Warning, Document, Files } from '@element-plus/icons-vue'
import request from '@/api/request'

const deviceChartRef = ref(null)
const faultChartRef = ref(null)
const orderChartRef = ref(null)
const trendChartRef = ref(null)

let charts = []

const summaryCards = reactive([
  { label: '设备总数', value: 0, icon: Monitor, bg: 'rgba(64,158,255,0.1)' },
  { label: '故障报告', value: 0, icon: Warning, bg: 'rgba(230,162,60,0.1)' },
  { label: '点检工单', value: 0, icon: Document, bg: 'rgba(103,194,58,0.1)' },
  { label: '知识文件', value: 0, icon: Files, bg: 'rgba(144,147,153,0.1)' }
])

async function fetchAll() {
  try {
    const [summaryRes, deviceRes, faultRes, orderRes, trendRes] = await Promise.all([
      request.get('/api/dashboard/summary'),
      request.get('/api/dashboard/device-status'),
      request.get('/api/dashboard/fault-status'),
      request.get('/api/dashboard/order-status'),
      request.get('/api/dashboard/monthly-trend')
    ])

    const s = summaryRes || {}
    summaryCards[0].value = s.device_count || 0
    summaryCards[1].value = s.fault_report_count || 0
    summaryCards[2].value = s.inspection_order_count || 0
    summaryCards[3].value = s.knowledge_file_count || 0

    renderPie(deviceChartRef, deviceRes || [], '设备状态')
    renderPie(faultChartRef, faultRes || [], '故障报告')
    renderPie(orderChartRef, orderRes || [], '工单状态')
    renderTrend(trendChartRef, trendRes || [])
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '获取统计数据失败')
  }
}

function renderPie(refEl, data, title) {
  if (!refEl.value) return
  const echarts = window._echarts
  if (!echarts) return
  const chart = echarts.init(refEl.value)
  charts.push(chart)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '48%'],
      label: { show: true, formatter: '{b}: {c}' },
      data: data.map(d => ({ name: d.status || d.name, value: d.count }))
    }]
  })
}

function renderTrend(refEl, data) {
  if (!refEl.value) return
  const echarts = window._echarts
  if (!echarts) return
  const chart = echarts.init(refEl.value)
  charts.push(chart)

  const months = data.map(d => d.month || '')
  const faults = data.map(d => d.fault_count || 0)
  const orders = data.map(d => d.order_count || 0)
  const maintenances = data.map(d => d.maintenance_count || 0)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value' },
    series: [
      { name: '故障', type: 'line', data: faults, smooth: true, itemStyle: { color: '#e6a23c' } },
      { name: '工单', type: 'line', data: orders, smooth: true, itemStyle: { color: '#67c23a' } },
      { name: '维保', type: 'line', data: maintenances, smooth: true, itemStyle: { color: '#409eff' } }
    ]
  })
}

onMounted(async () => {
  const echarts = (await import('echarts')).default || (await import('echarts'))
  window._echarts = echarts
  window.addEventListener('resize', () => charts.forEach(c => c?.resize()))
  await fetchAll()
})

onBeforeUnmount(() => {
  charts.forEach(c => c?.dispose())
  charts = []
})
</script>

<style scoped>
.admin-stats-page h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
  color: #303133;
}

.card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.card-label {
  font-size: 0.85rem;
  color: #909399;
  margin-top: 2px;
}
</style>
