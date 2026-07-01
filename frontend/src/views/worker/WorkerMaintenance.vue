<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>维保记录与自检报告</span>
          <el-button type="primary" @click="openGenerateDialog">生成维保记录</el-button>
        </div>
      </template>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="id" label="编号" width="60" />
        <el-table-column prop="record_no" label="记录编号" min-width="160" show-overflow-tooltip />
        <el-table-column prop="device_name" label="设备" min-width="120" show-overflow-tooltip />
        <el-table-column prop="device_code" label="设备编号" min-width="120" show-overflow-tooltip />
        <el-table-column label="点检类型" width="90">
          <template #default="{ row }">
            {{ getInspectionTypeLabel(row.inspection_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="conclusion" label="维保结论" min-width="200" show-overflow-tooltip />
        <el-table-column label="生成时间" width="170">
          <template #default="{ row }">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="preview(row)">详情</el-button>
            <el-button size="small" type="success" @click="downloadReport(row)">报告</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 生成维保记录对话框 -->
    <el-dialog v-model="generateVisible" title="生成维保记录" width="560px" destroy-on-close>
      <div v-loading="ordersLoading">
        <el-form label-width="100px">
          <el-form-item label="已完成工单" required>
            <el-select
              v-model="selectedOrderId"
              filterable
              placeholder="请选择已完成点检工单"
              style="width:100%"
            >
              <el-option
                v-for="order in completedOrders"
                :key="order.id"
                :label="`${order.order_no || '工单' + order.id} - ${order.order_name || '未命名'}`"
                :value="order.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <el-empty v-if="!ordersLoading && completedOrders.length === 0" description="暂无已完成点检工单" :image-size="80" />
      </div>
      <template #footer>
        <el-button @click="generateVisible = false">取消</el-button>
        <el-button type="primary" :loading="generateLoading" @click="handleGenerate">确认生成</el-button>
      </template>
    </el-dialog>

    <!-- 维保记录详情对话框 -->
    <el-dialog v-model="previewVisible" title="维保记录详情" width="700px">
      <el-descriptions :column="2" border v-if="previewItem">
        <el-descriptions-item label="记录编号">{{ previewItem.record_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工单编号">{{ previewItem.order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ previewItem.device_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备编号">{{ previewItem.device_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维保单位">{{ previewItem.maintenance_company || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ previewItem.responsible_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="项目总数">{{ previewItem.total_items ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="正常">{{ previewItem.normal_items ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="异常">{{ previewItem.abnormal_items ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="不适用">{{ previewItem.not_applicable_items ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="维保结论" :span="2">{{ previewItem.conclusion || '-' }}</el-descriptions-item>
        <el-descriptions-item label="生成时间">{{ fmt(previewItem.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 维保报告对话框 -->
    <el-dialog v-model="reportVisible" title="维保报告" width="800px" v-loading="reportLoading">
      <div v-if="reportContent" style="white-space:pre-wrap;line-height:1.8;max-height:500px;overflow-y:auto">
        <h3 style="text-align:center;margin-bottom:12px">电梯/扶梯维保自检报告</h3>
        <div style="color:#6b778c;text-align:center;margin-bottom:16px;font-size:13px">
          记录编号：{{ reportRecordNo }}
        </div>
        <div style="border-top:1px solid #edf1f7;padding-top:16px">{{ reportContent }}</div>
      </div>
      <el-empty v-else description="暂无报告内容" :image-size="80" />
      <template #footer>
        <el-button v-if="reportContent" @click="copyReport">复制报告</el-button>
        <el-button @click="reportVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const inspectionTypeOptions = [
  { label: '日检', value: 'daily' },
  { label: '月检', value: 'monthly' },
  { label: '季检', value: 'quarterly' },
  { label: '年检', value: 'annual' },
  { label: '故障检修', value: 'fault' }
]

function getInspectionTypeLabel(value) {
  return inspectionTypeOptions.find((item) => item.value === value)?.label || value || '-'
}

const records = ref([])
const loading = ref(false)
const previewVisible = ref(false)
const previewItem = ref(null)
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportContent = ref('')
const reportRecordNo = ref('')
const generateVisible = ref(false)
const generateLoading = ref(false)
const ordersLoading = ref(false)
const completedOrders = ref([])
const selectedOrderId = ref(null)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

function fmt(s) { return s ? s.slice(0, 10) : '' }

async function fetchRecords() {
  loading.value = true
  try {
    const res = await request.get('/api/maintenance/records', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size
      }
    })
    records.value = res?.items || []
    pagination.total = res?.total || 0
  } catch {} finally { loading.value = false }
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchRecords()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchRecords()
}

async function fetchCompletedOrders() {
  ordersLoading.value = true
  try {
    const res = await request.get('/api/inspections/orders', {
      params: { page: 1, page_size: 100, status: 'completed' }
    })
    completedOrders.value = res?.items || []
  } catch {} finally { ordersLoading.value = false }
}

function openGenerateDialog() {
  selectedOrderId.value = null
  generateVisible.value = true
  fetchCompletedOrders()
}

async function handleGenerate() {
  if (!selectedOrderId.value) {
    ElMessage.warning('请选择已完成点检工单')
    return
  }
  generateLoading.value = true
  try {
    await request.post(`/api/maintenance/records/from-order/${selectedOrderId.value}`)
    ElMessage.success('维保记录生成成功')
    generateVisible.value = false
    pagination.page = 1
    await fetchRecords()
  } catch {
    ElMessage.error('生成失败')
  } finally { generateLoading.value = false }
}

function preview(row) {
  previewItem.value = row
  previewVisible.value = true
}

async function downloadReport(row) {
  reportVisible.value = true
  reportLoading.value = true
  reportContent.value = ''
  reportRecordNo.value = row.record_no || ''
  try {
    const res = await request.get(`/api/maintenance/records/${row.id}/report`)
    reportContent.value = res?.report_content || ''
  } catch {
    reportContent.value = ''
  } finally { reportLoading.value = false }
}

async function copyReport() {
  if (!reportContent.value) return
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(reportContent.value)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = reportContent.value
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'fixed'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    ElMessage.success('报告正文已复制')
  } catch {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

onMounted(fetchRecords)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
