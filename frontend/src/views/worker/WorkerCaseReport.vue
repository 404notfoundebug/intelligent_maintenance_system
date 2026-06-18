<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>故障案例上报</span>
          <el-button type="primary" @click="showReport">上报新案例</el-button>
        </div>
      </template>
      <el-table :data="cases" v-loading="loading" stripe>
        <el-table-column prop="id" label="编号" width="60" />
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="device_name" label="关联设备" min-width="120" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上报时间" width="100">
          <template #default="{ row }">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="reportVisible" title="上报故障案例" width="600px">
      <el-form :model="reportForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="reportForm.title" /></el-form-item>
        <el-form-item label="设备">
          <el-select v-model="reportForm.device_id" placeholder="选择设备" style="width:100%">
            <el-option v-for="d in devices" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="故障描述">
          <el-input v-model="reportForm.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="故障分类">
          <el-select v-model="reportForm.category" placeholder="选择分类" style="width:100%">
            <el-option label="机械故障" value="机械故障" />
            <el-option label="电气故障" value="电气故障" />
            <el-option label="控制系统" value="控制系统" />
            <el-option label="安全装置" value="安全装置" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReport" :loading="submitting">提交审核</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="案例详情" width="600px">
      <el-descriptions :column="1" border v-if="detailItem">
        <el-descriptions-item label="标题">{{ detailItem.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备">{{ detailItem.device_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ detailItem.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTag(detailItem.status)" size="small">{{ statusText(detailItem.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="上报时间">{{ fmt(detailItem.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="故障描述">{{ detailItem.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核意见">{{ detailItem.audit_comment || '暂无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const cases = ref([])
const devices = ref([])
const loading = ref(false)
const submitting = ref(false)
const reportVisible = ref(false)
const detailVisible = ref(false)
const detailItem = ref(null)
const reportForm = ref({ title: '', device_id: null, description: '', category: '' })

function fmt(s) { return s ? s.slice(0, 10) : '' }
function statusText(s) { return { pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s || '待审核' }
function statusTag(s) { return { pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'warning' }

async function fetchData() {
  loading.value = true
  try {
    const [r1, r2] = await Promise.all([
      request.get('/api/cases'),
      request.get('/api/devices')
    ])
    cases.value = r1?.items || r1 || []
    devices.value = r2 || []
  } catch {} finally { loading.value = false }
}

onMounted(fetchData)

function showReport() { reportForm.value = { title: '', device_id: null, description: '', category: '' }; reportVisible.value = true }

async function submitReport() {
  submitting.value = true
  try {
    await request.post('/api/cases', reportForm.value)
    ElMessage.success('上报成功，等待审核')
    reportVisible.value = false
    await fetchData()
  } catch { ElMessage.error('上报失败') } finally { submitting.value = false }
}

function showDetail(row) {
  detailItem.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
