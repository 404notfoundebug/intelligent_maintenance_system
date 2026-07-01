<template>
  <div class="page maintenance-page">
    <div class="page-header">
      <div>
        <h1>维保记录</h1>
        <p>将已完成点检工单转化为标准化维保记录与自检报告，便于归档、追溯和展示。</p>
      </div>
      <el-button type="primary" @click="openGenerateDialog">生成维保记录</el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" class="filter-form" label-width="80px">
        <el-form-item label="关键词">
          <el-input
            v-model.trim="queryForm.keyword"
            clearable
            placeholder="请输入记录编号/设备名称/设备编号"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="点检类型">
          <el-select v-model="queryForm.inspection_type" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in inspectionTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openGenerateDialog">生成维保记录</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="recordList"
        row-key="id"
        border
        stripe
        class="maintenance-table"
      >
        <el-table-column prop="record_no" label="记录编号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="device_name" label="设备名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="device_code" label="设备编号" min-width="120" show-overflow-tooltip />
        <el-table-column label="设备类型" min-width="120">
          <template #default="{ row }">
            {{ getDeviceTypeLabel(row.device_type) }}
          </template>
        </el-table-column>
        <el-table-column label="点检类型" width="110">
          <template #default="{ row }">
            {{ getInspectionTypeLabel(row.inspection_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="工单编号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="total_items" label="总数" width="80" />
        <el-table-column prop="normal_items" label="正常" width="80" />
        <el-table-column label="异常" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.abnormal_items > 0" type="danger" effect="light">
              {{ row.abnormal_items }}
            </el-tag>
            <span v-else>{{ row.abnormal_items }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="conclusion" label="维保结论" min-width="220" show-overflow-tooltip />
        <el-table-column label="生成时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="210">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetailDialog(row)">查看详情</el-button>
            <el-button link type="primary" @click="openReportDialog(row)">查看报告</el-button>
            <el-button v-if="canDeleteRecord" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog
      v-model="generateDialogVisible"
      title="生成维保记录"
      width="620px"
      destroy-on-close
      @closed="resetGenerateForm"
    >
      <div v-loading="completedOrdersLoading">
        <el-form :model="generateForm" label-width="100px">
          <el-form-item label="已完成工单" required>
            <el-select
              v-model="generateForm.order_id"
              filterable
              placeholder="请选择已完成点检工单"
              class="full-select"
            >
              <el-option
                v-for="order in completedOrders"
                :key="order.id"
                :label="formatOrderOption(order)"
                :value="order.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <el-empty
          v-if="!completedOrdersLoading && completedOrders.length === 0"
          description="暂无已完成点检工单"
        />
      </div>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="generateLoading" @click="handleGenerateRecord">
          确认生成
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="维保记录详情" width="750px">
      <div v-loading="detailLoading" class="detail-body">
        <el-descriptions v-if="detailData" :column="2" border>
          <el-descriptions-item label="记录编号">{{ displayValue(detailData.record_no) }}</el-descriptions-item>
          <el-descriptions-item label="工单编号">{{ displayValue(detailData.order_no) }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ displayValue(detailData.device_name) }}</el-descriptions-item>
          <el-descriptions-item label="设备编号">{{ displayValue(detailData.device_code) }}</el-descriptions-item>
          <el-descriptions-item label="设备类型">{{ getDeviceTypeLabel(detailData.device_type) }}</el-descriptions-item>
          <el-descriptions-item label="维保单位">{{ displayValue(detailData.maintenance_company) }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ displayValue(detailData.responsible_person) }}</el-descriptions-item>
          <el-descriptions-item label="点检类型">{{ getInspectionTypeLabel(detailData.inspection_type) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(detailData.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(detailData.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="项目总数">{{ displayValue(detailData.total_items) }}</el-descriptions-item>
          <el-descriptions-item label="正常项目">{{ displayValue(detailData.normal_items) }}</el-descriptions-item>
          <el-descriptions-item label="异常项目">
            <el-tag v-if="detailData.abnormal_items > 0" type="danger" effect="light">
              {{ detailData.abnormal_items }}
            </el-tag>
            <span v-else>{{ displayValue(detailData.abnormal_items) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="不适用项目">{{ displayValue(detailData.not_applicable_items) }}</el-descriptions-item>
          <el-descriptions-item label="生成时间">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="维保结论" :span="2">
            {{ displayValue(detailData.conclusion) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <el-dialog v-model="reportDialogVisible" title="自检报告预览" width="900px">
      <div v-loading="reportLoading" class="report-dialog-body">
        <div v-if="reportData" class="report-document">
          <h2>电梯/扶梯维保自检报告</h2>
          <div class="report-meta">记录编号：{{ reportData.record_no }}</div>
          <div class="report-content">{{ reportData.report_content || '暂无报告正文' }}</div>
        </div>
      </div>
      <template #footer>
        <el-button :disabled="!reportData?.report_content" @click="copyReport">复制报告</el-button>
        <el-button :disabled="!reportData?.report_content" @click="exportPDF">导出PDF</el-button>
        <el-button :disabled="!reportData?.report_content" @click="exportWord">导出Word</el-button>
        <el-button type="primary" @click="reportDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../../stores/user'
import { getInspectionOrders } from '../../api/inspections'
import {
  deleteMaintenanceRecord,
  generateMaintenanceRecordFromOrder,
  getMaintenanceRecordDetail,
  getMaintenanceRecords,
  getMaintenanceReport
} from '../../api/maintenance'

const userStore = useUserStore()

const deviceTypeOptions = [
  { label: '曳引电梯', value: 'traction_elevator' },
  { label: '液压电梯', value: 'hydraulic_elevator' },
  { label: '自动扶梯', value: 'escalator' },
  { label: '自动人行道', value: 'moving_walkway' }
]

const inspectionTypeOptions = [
  { label: '日检', value: 'daily' },
  { label: '月检', value: 'monthly' },
  { label: '季检', value: 'quarterly' },
  { label: '年检', value: 'annual' },
  { label: '故障检修', value: 'fault' }
]

const queryForm = reactive({
  keyword: '',
  inspection_type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loading = ref(false)
const recordList = ref([])
const generateDialogVisible = ref(false)
const generateLoading = ref(false)
const completedOrdersLoading = ref(false)
const completedOrders = ref([])
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
const reportDialogVisible = ref(false)
const reportLoading = ref(false)
const reportData = ref(null)

const generateForm = reactive({
  order_id: null
})

const currentRole = computed(() => userStore.userInfo?.role || '')
const canDeleteRecord = computed(() => currentRole.value === 'admin')

function displayValue(value) {
  return value === 0 ? 0 : value || '-'
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function getOptionLabel(options, value) {
  return options.find((item) => item.value === value)?.label || value || '-'
}

function getDeviceTypeLabel(value) {
  return getOptionLabel(deviceTypeOptions, value)
}

function getInspectionTypeLabel(value) {
  return getOptionLabel(inspectionTypeOptions, value)
}

function formatOrderOption(order) {
  return `${order.order_no || `工单${order.id}`} - ${order.order_name || '未命名工单'}`
}

async function fetchRecordList() {
  loading.value = true
  try {
    const data = await getMaintenanceRecords({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: queryForm.keyword,
      inspection_type: queryForm.inspection_type
    })
    recordList.value = data?.items || []
    pagination.total = data?.total || 0
    pagination.page = data?.page || pagination.page
    pagination.page_size = data?.page_size || pagination.page_size
  } catch (error) {
    recordList.value = []
  } finally {
    loading.value = false
  }
}

async function fetchCompletedOrders() {
  completedOrdersLoading.value = true
  try {
    const data = await getInspectionOrders({
      page: 1,
      page_size: 100,
      status: 'completed'
    })
    completedOrders.value = data?.items || []
  } catch (error) {
    completedOrders.value = []
  } finally {
    completedOrdersLoading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchRecordList()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.inspection_type = ''
  pagination.page = 1
  fetchRecordList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchRecordList()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchRecordList()
}

async function openGenerateDialog() {
  resetGenerateForm()
  generateDialogVisible.value = true
  await fetchCompletedOrders()
}

function resetGenerateForm() {
  generateForm.order_id = null
}

async function handleGenerateRecord() {
  if (!generateForm.order_id) {
    ElMessage.warning('请选择已完成点检工单')
    return
  }

  const knownExisting = recordList.value.some((record) => record.order_id === generateForm.order_id)
  generateLoading.value = true
  try {
    await generateMaintenanceRecordFromOrder(generateForm.order_id)
    if (knownExisting) {
      ElMessage.warning('该工单已生成维保记录')
    } else {
      ElMessage.success('维保记录生成成功')
    }
    generateDialogVisible.value = false
    pagination.page = 1
    await fetchRecordList()
  } catch (error) {
    // request.js already shows backend errors.
  } finally {
    generateLoading.value = false
  }
}

async function openDetailDialog(row) {
  detailDialogVisible.value = true
  detailLoading.value = true
  detailData.value = null
  try {
    detailData.value = await getMaintenanceRecordDetail(row.id)
  } catch (error) {
    ElMessage.error('获取维保记录详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function openReportDialog(row) {
  reportDialogVisible.value = true
  reportLoading.value = true
  reportData.value = null
  try {
    reportData.value = await getMaintenanceReport(row.id)
  } catch (error) {
    ElMessage.error('获取自检报告失败')
  } finally {
    reportLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除维保记录“${row.record_no}”吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteMaintenanceRecord(row.id)
    ElMessage.success('维保记录删除成功')
    if (recordList.value.length === 1 && pagination.page > 1) {
      pagination.page -= 1
    }
    await fetchRecordList()
  } catch (error) {
    if (error !== 'cancel') {
      // request.js already shows backend errors.
    }
  }
}

async function copyReport() {
  const content = reportData.value?.report_content
  if (!content) return

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(content)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = content
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'fixed'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    ElMessage.success('报告正文已复制')
  } catch (error) {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}

function showExportTip() {
  ElMessage.info('导出功能后续开发')
}

function exportPDF() {
  const content = reportData.value?.report_content
  if (!content) return

  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    ElMessage.error('请允许浏览器弹出窗口以导出PDF')
    return
  }

  const recordNo = reportData.value?.record_no || '维保报告'
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>${recordNo}</title>
      <style>
        body { font-family: "Microsoft YaHei", "SimSun", sans-serif; padding: 40px 50px; line-height: 1.8; color: #333; }
        h1 { text-align: center; font-size: 22px; margin-bottom: 10px; }
        .meta { text-align: center; color: #666; font-size: 13px; margin-bottom: 24px; border-bottom: 1px solid #ddd; padding-bottom: 12px; }
        .content { white-space: pre-wrap; word-break: break-word; font-size: 14px; }
        @media print { body { padding: 20px 30px; } }
      </style>
    </head>
    <body>
      <h1>电梯/扶梯维保自检报告</h1>
      <div class="meta">记录编号：${recordNo}</div>
      <div class="content">${content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')}</div>
    </body>
    </html>
  `)
  printWindow.document.close()
  printWindow.focus()
  setTimeout(() => {
    printWindow.print()
  }, 500)
}

function exportWord() {
  const content = reportData.value?.report_content
  if (!content) return

  const recordNo = reportData.value?.record_no || '维保报告'
  const htmlContent = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office"
          xmlns:w="urn:schemas-microsoft-com:office:word"
          xmlns="http://www.w3.org/TR/REC-html40">
    <head>
      <meta charset="utf-8" />
      <title>${recordNo}</title>
      <style>
        body { font-family: "Microsoft YaHei", "SimSun", sans-serif; padding: 30px; line-height: 1.8; }
        h1 { text-align: center; font-size: 20px; }
        .meta { text-align: center; color: #666; font-size: 12px; margin-bottom: 20px; }
        .content { white-space: pre-wrap; font-size: 14px; }
      </style>
    </head>
    <body>
      <h1>电梯/扶梯维保自检报告</h1>
      <div class="meta">记录编号：${recordNo}</div>
      <div class="content">${content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
    </body>
    </html>
  `

  const blob = new Blob(['\ufeff' + htmlContent], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${recordNo}.doc`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('Word 文档已下载')
}

onMounted(() => {
  fetchRecordList()
})
</script>

<style scoped>
.maintenance-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.filter-card,
.table-card {
  border: 1px solid rgba(30, 92, 180, 0.08);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(16, 41, 84, 0.06);
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(180px, 260px) auto;
  gap: 14px;
  align-items: center;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
}

.maintenance-table {
  width: 100%;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.full-select {
  width: 100%;
}

.detail-body {
  min-height: 260px;
}

.report-dialog-body {
  min-height: 420px;
}

.report-document {
  background: #ffffff;
  border: 1px solid #e6edf7;
  border-radius: 10px;
  box-shadow: inset 0 1px 0 rgba(47, 111, 237, 0.04);
  color: #25344d;
  max-height: 620px;
  overflow-y: auto;
  padding: 24px 28px;
}

.report-document h2 {
  color: #14233f;
  font-size: 22px;
  margin: 0 0 10px;
  text-align: center;
}

.report-meta {
  color: #6b778c;
  font-size: 13px;
  margin-bottom: 18px;
  text-align: center;
}

.report-content {
  border-top: 1px solid #edf1f7;
  line-height: 1.85;
  padding-top: 18px;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 1180px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(240px, 1fr));
  }
}

@media (max-width: 760px) {
  .filter-form {
    grid-template-columns: 1fr;
  }

  .pagination-wrap {
    justify-content: flex-start;
    overflow-x: auto;
  }
}
</style>
