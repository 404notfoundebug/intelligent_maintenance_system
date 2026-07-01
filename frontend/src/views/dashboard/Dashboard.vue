<template>
  <div class="page dashboard-page">
    <div class="page-header">
      <div>
        <h1>首页看板</h1>
        <p>欢迎回来，{{ userName }}。这里汇总展示系统运行概况与关键业务数据。</p>
      </div>
      <el-button type="primary" :loading="loading" @click="loadSummary">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <el-alert
      v-if="errorText"
      class="dashboard-alert"
      type="error"
      :title="errorText"
      show-icon
      :closable="false"
    />

    <div class="metric-grid">
      <el-card v-for="item in metrics" :key="item.label" class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon" :class="item.tone">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div>
            <div class="metric-value">{{ item.value }}</div>
            <div class="metric-label">{{ item.label }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="dashboard-section">
      <el-card shadow="never" class="summary-card">
        <template #header>
          <div class="card-header">
            <span>运行概览</span>
            <el-tag type="primary">实时统计</el-tag>
          </div>
        </template>
        <div class="summary-list">
          <div class="summary-row">
            <span>正常设备</span>
            <strong>{{ summary.normal_device_count || 0 }}</strong>
          </div>
          <div class="summary-row">
            <span>故障设备</span>
            <strong>{{ summary.fault_device_count || 0 }}</strong>
          </div>
          <div class="summary-row">
            <span>维保中设备</span>
            <strong>{{ summary.maintenance_device_count || 0 }}</strong>
          </div>
          <div class="summary-row">
            <span>待审核案例</span>
            <strong>{{ summary.pending_case_count || 0 }}</strong>
          </div>
        </div>
      </el-card>

      <el-card shadow="never" class="summary-card">
        <template #header>
          <div class="card-header">
            <span>业务闭环</span>
            <el-tag type="success">知识复用</el-tag>
          </div>
        </template>
        <div class="flow-line">
          <span>故障上报</span>
          <i />
          <span>智能建议</span>
          <i />
          <span>点检工单</span>
          <i />
          <span>维保记录</span>
          <i />
          <span>案例入库</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getDashboardSummary } from '../../api/dashboard'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const loading = ref(false)
const errorText = ref('')
const summary = ref({})

const userName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '用户')

const metrics = computed(() => [
  { label: '设备总数', value: summary.value.device_count || 0, icon: 'Cpu', tone: 'blue' },
  { label: '故障上报', value: summary.value.fault_report_count || 0, icon: 'Warning', tone: 'red' },
  { label: '待处理故障', value: summary.value.pending_fault_count || 0, icon: 'Bell', tone: 'orange' },
  { label: '点检工单', value: summary.value.inspection_order_count || 0, icon: 'Checked', tone: 'green' },
  { label: '已完成工单', value: summary.value.completed_order_count || 0, icon: 'CircleCheck', tone: 'cyan' },
  { label: '维保记录', value: summary.value.maintenance_record_count || 0, icon: 'DocumentChecked', tone: 'purple' },
  { label: '知识库文档', value: summary.value.knowledge_file_count || 0, icon: 'Collection', tone: 'blue' },
  { label: '检修案例', value: summary.value.repair_case_count || 0, icon: 'Notebook', tone: 'green' }
])

async function loadSummary() {
  loading.value = true
  errorText.value = ''
  try {
    summary.value = await getDashboardSummary()
  } catch (error) {
    errorText.value = 'Dashboard 数据加载失败，请确认后端服务和登录状态正常。'
    ElMessage.error(errorText.value)
  } finally {
    loading.value = false
  }
}

onMounted(loadSummary)
</script>
