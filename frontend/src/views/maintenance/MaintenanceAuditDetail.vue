<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button text @click="$router.push('/admin/maintenance-audit')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <span>维保审核详情</span>
        </div>
      </template>

      <div v-if="loading" v-loading="true" style="min-height:200px" />
      <div v-else-if="record">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="记录编号">{{ record.record_no }}</el-descriptions-item>
          <el-descriptions-item label="关联工单">{{ record.order_no }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ record.device_name }}</el-descriptions-item>
          <el-descriptions-item label="设备编号">{{ record.device_code }}</el-descriptions-item>
          <el-descriptions-item label="设备类型">{{ deviceTypeMap[record.device_type] || record.device_type }}</el-descriptions-item>
          <el-descriptions-item label="维保单位">{{ record.maintenance_company || '—' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ record.responsible_person || '—' }}</el-descriptions-item>
          <el-descriptions-item label="点检类型">{{ inspectionTypeMap[record.inspection_type] || record.inspection_type }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ record.start_time?.slice(0, 19).replace('T', ' ') || '—' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ record.end_time?.slice(0, 19).replace('T', ' ') || '—' }}</el-descriptions-item>
          <el-descriptions-item label="总项数">{{ record.total_items }}</el-descriptions-item>
          <el-descriptions-item label="正常/异常/不适用">{{ record.normal_items }} / {{ record.abnormal_items }} / {{ record.not_applicable_items }}</el-descriptions-item>
          <el-descriptions-item label="结论">{{ record.conclusion || '—' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 审核报告 -->
        <div style="margin-top: 24px;" v-if="reportContent">
          <h3 style="margin-bottom: 12px; color: #303133;">AI 生成审核报告</h3>
          <div class="report-content" v-html="formattedReport"></div>
        </div>
        <div v-else style="margin-top: 24px;">
          <el-alert type="info" :closable="false">暂无审核报告，请先生成报告。</el-alert>
        </div>

        <div style="margin-top: 24px; display:flex; gap:12px;">
          <el-button @click="$router.push('/admin/maintenance-audit')">返回列表</el-button>
          <el-button type="primary" :loading="generating" @click="handleGenerateReport">生成/刷新报告</el-button>
          <el-button type="success" @click="handleApprove">审核通过</el-button>
          <el-button type="danger" @click="handleReject">审核驳回</el-button>
        </div>
      </div>
      <el-empty v-else description="记录不存在" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const record = ref(null)
const reportContent = ref('')
const generating = ref(false)

const deviceTypeMap = {
  traction_elevator: '曳引电梯',
  hydraulic_elevator: '液压电梯',
  escalator: '自动扶梯',
  moving_walkway: '自动人行道'
}
const inspectionTypeMap = {
  daily: '日常点检',
  monthly: '月度点检',
  quarterly: '季度点检',
  annual: '年度点检',
  fault: '故障点检'
}

const formattedReport = computed(() => {
  if (!reportContent.value) return ''
  return reportContent.value
    .replace(/\n/g, '<br>')
    .replace(/#{1,3} (.+)/g, '<strong>$1</strong>')
})

async function fetchRecord() {
  loading.value = true
  try {
    const res = await request.get(`/api/maintenance/records/${route.params.id}`)
    record.value = res || {}
  } catch {
    ElMessage.error('获取记录详情失败')
  } finally {
    loading.value = false
  }
}

async function fetchReport() {
  try {
    const res = await request.get(`/api/maintenance/records/${route.params.id}/report`)
    reportContent.value = res?.report_content || ''
  } catch {
    // 报告可能尚未生成
  }
}

async function handleGenerateReport() {
  if (!record.value?.order_id) {
    ElMessage.warning('该记录缺少关联工单ID，无法生成报告')
    return
  }
  generating.value = true
  try {
    await request.post(`/api/maintenance/records/from-order/${record.value.order_id}`)
    await fetchReport()
    ElMessage.success('报告生成成功')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '生成报告失败')
  } finally {
    generating.value = false
  }
}

async function handleApprove() {
  try {
    await ElMessageBox.confirm('确认审核通过该维保记录？', '提示', { type: 'success' })
    await request.put(`/api/maintenance/records/${route.params.id}/audit`, { status: 'approved' })
    ElMessage.success('审核通过')
    fetchRecord()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

async function handleReject() {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '审核驳回', {
      inputType: 'textarea',
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消'
    })
    await request.put(`/api/maintenance/records/${route.params.id}/audit`, { status: 'rejected', reject_reason: value })
    ElMessage.success('已驳回')
    fetchRecord()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

onMounted(() => {
  fetchRecord()
  fetchReport()
})
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; align-items: center; gap: 12px; }
.report-content {
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
  white-space: pre-wrap;
}
</style>
