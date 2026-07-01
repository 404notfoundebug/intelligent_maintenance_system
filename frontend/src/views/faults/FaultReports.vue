<template>
  <div class="fault-reports-page">
    <div class="page-header">
      <div>
        <h1>多模态故障检索</h1>
        <p>故障记录、现场图片上传和状态管理</p>
      </div>
      <el-button type="primary" @click="openCreate">上报故障</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="故障描述/设备名称" clearable style="width:220px" @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable placeholder="全部" style="width:140px">
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 故障列表 -->
    <el-table :data="faults" v-loading="loading" stripe border style="width:100%;margin-top:16px">
      <el-table-column prop="report_no" label="编号" width="140" />
      <el-table-column prop="device_name" label="设备名称" min-width="140" show-overflow-tooltip />
      <el-table-column prop="device_model" label="设备型号" width="120" />
      <el-table-column prop="fault_description" label="故障描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="fault_code" label="故障代码" width="110">
        <template #default="{ row }">{{ row.fault_code || '-' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.status]?.type || 'info'" size="small">
            {{ statusMap[row.status]?.label || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="submitted_by" label="提交人" width="100" />
      <el-table-column prop="created_at" label="上报时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">详情</el-button>
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="warning"
            @click="updateStatus(row, 'processing')"
          >处理</el-button>
          <el-button
            v-if="row.status === 'processing'"
            size="small"
            type="success"
            @click="updateStatus(row, 'resolved')"
          >解决</el-button>
          <el-button
            size="small"
            type="primary"
            :disabled="!!row.advice_record_id"
            @click="generateAdvice(row)"
          >生成建议</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchFaults"
        @current-change="fetchFaults"
      />
    </div>

    <!-- 新建/编辑 Dialog -->
    <el-dialog
      v-model="createVisible"
      title="上报故障"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top">
        <el-form-item label="设备名称" prop="device_name">
          <el-input v-model="createForm.device_name" placeholder="请输入设备名称" maxlength="100" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="设备型号">
              <el-input v-model="createForm.device_model" placeholder="如 TX-1000" maxlength="64" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="故障代码">
              <el-input v-model="createForm.fault_code" placeholder="如 E35" maxlength="32" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="故障描述" prop="fault_description">
          <el-input
            v-model="createForm.fault_description"
            type="textarea"
            :rows="5"
            maxlength="1000"
            show-word-limit
            placeholder="请详细描述故障现象"
          />
        </el-form-item>
        <el-form-item label="故障位置">
          <el-input v-model="createForm.location" placeholder="如 3号梯机房" maxlength="200" />
        </el-form-item>
        <el-form-item label="现场图片">
          <el-upload
            :auto-upload="false"
            :limit="5"
            list-type="picture-card"
            accept="image/*"
            :on-change="handleImageChange"
            :file-list="imageList"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-hint">支持 jpg/png/webp，最多 5 张</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleCreate">提交</el-button>
      </template>
    </el-dialog>

    <!-- 详情 Dialog -->
    <el-dialog v-model="detailVisible" title="故障详情" width="700px">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="编号">{{ detail.report_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ detail.device_name }}</el-descriptions-item>
          <el-descriptions-item label="设备型号">{{ detail.device_model || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障代码">{{ detail.fault_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障位置">{{ detail.location || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障描述" :span="2">{{ detail.fault_description }}</el-descriptions-item>
          <el-descriptions-item label="提交人">{{ detail.submitted_by }}</el-descriptions-item>
          <el-descriptions-item label="上报时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detail.images && detail.images.length" class="detail-images">
          <h4>现场图片 ({{ detail.images.length }})</h4>
          <div class="image-grid">
            <el-image
              v-for="img in detail.images"
              :key="img.id"
              :src="img.image_url"
              :preview-src-list="detail.images.map(i => i.image_url)"
              fit="cover"
              class="detail-image-item"
            />
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 检修建议 Dialog -->
    <el-dialog v-model="adviceVisible" title="生成检修建议" width="600px">
      <div v-if="adviceLoading" class="advice-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在生成检修建议...</span>
      </div>
      <div v-else-if="adviceResult">
        <div class="advice-answer">{{ adviceResult.answer }}</div>
        <el-divider />
        <h4>参考知识来源 ({{ adviceResult.references?.length || 0 }})</h4>
        <el-table v-if="adviceResult.references?.length" :data="adviceResult.references" size="small" border>
          <el-table-column prop="source_file_name" label="来源文件" show-overflow-tooltip />
          <el-table-column label="相关度" width="90">
            <template #default="{ row }">{{ row.score?.toFixed?.(2) || row.score }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Loading } from '@element-plus/icons-vue'
import { getFaultReports, getFaultDetail, createFaultReport, updateFaultStatus, deleteFault } from '@/api/faults'
import request from '@/api/request'

const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' }
]

const statusMap = {
  pending: { label: '待处理', type: 'warning' },
  processing: { label: '处理中', type: 'primary' },
  resolved: { label: '已解决', type: 'success' },
  closed: { label: '已关闭', type: 'info' }
}

const faults = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const searchForm = reactive({ keyword: '', status: '' })

// 新建
const createVisible = ref(false)
const saving = ref(false)
const createFormRef = ref(null)
const imageList = ref([])
const pendingFiles = ref([])

const createForm = reactive({
  device_name: '',
  device_model: '',
  fault_code: '',
  fault_description: '',
  location: ''
})

const createRules = {
  device_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  fault_description: [{ required: true, message: '请输入故障描述', trigger: 'blur' }]
}

// 详情
const detailVisible = ref(false)
const detail = ref(null)

// 检修建议
const adviceVisible = ref(false)
const adviceLoading = ref(false)
const adviceResult = ref(null)

function formatTime(str) {
  if (!str) return '-'
  return new Date(str).toLocaleString('zh-CN')
}

async function fetchFaults() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.status) params.status = searchForm.status
    const res = await getFaultReports(params)
    faults.value = res.items || []
    pagination.total = res.total || 0
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '获取故障列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchFaults()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.status = ''
  pagination.page = 1
  fetchFaults()
}

function openCreate() {
  createForm.device_name = ''
  createForm.device_model = ''
  createForm.fault_code = ''
  createForm.fault_description = ''
  createForm.location = ''
  imageList.value = []
  pendingFiles.value = []
  createVisible.value = true
}

function handleImageChange(file) {
  pendingFiles.value.push(file.raw)
}

async function handleCreate() {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const res = await createFaultReport({
      device_name: createForm.device_name,
      device_model: createForm.device_model || undefined,
      fault_code: createForm.fault_code || undefined,
      fault_description: createForm.fault_description,
      location: createForm.location || undefined
    })
    const faultId = res?.id
    // 上传图片
    if (faultId && pendingFiles.value.length) {
      for (const file of pendingFiles.value) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('image_type', 'scene')
        await request.post(`/api/faults/${faultId}/images`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }
    }
    ElMessage.success('故障上报成功')
    createVisible.value = false
    fetchFaults()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.response?.data?.detail || '上报失败')
  } finally {
    saving.value = false
  }
}

async function openDetail(row) {
  try {
    const res = await getFaultDetail(row.id)
    detail.value = res || row
    detailVisible.value = true
  } catch (err) {
    ElMessage.error('获取故障详情失败')
  }
}

async function updateStatus(row, status) {
  try {
    await updateFaultStatus(row.id, { status })
    ElMessage.success('状态更新成功')
    fetchFaults()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '状态更新失败')
  }
}

async function generateAdvice(row) {
  adviceVisible.value = true
  adviceLoading.value = true
  adviceResult.value = null
  try {
    const res = await request.post(`/api/faults/${row.id}/repair-advice?top_k=5`)
    adviceResult.value = res || {}
  } catch (err) {
    ElMessage.error('生成建议失败')
    adviceVisible.value = false
  } finally {
    adviceLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除故障记录「${row.report_no}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await deleteFault(row.id)
    ElMessage.success('删除成功')
    fetchFaults()
  } catch (err) {
    if (err !== 'cancel' && err?.response) {
      ElMessage.error(err?.response?.data?.message || '删除失败')
    }
  }
}

onMounted(fetchFaults)
</script>

<style scoped>
.fault-reports-page { padding: 0; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h1 { margin: 0; font-size: 1.25rem; color: #303133; }
.page-header p { margin: 4px 0 0; font-size: 13px; color: #909399; }

.search-card { margin-bottom: 0; border-radius: 10px; }
.search-card :deep(.el-card__body) { padding: 16px 20px 4px; }

.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }

.upload-hint { font-size: 12px; color: #909399; margin-top: 4px; }

.detail-images { margin-top: 20px; }
.detail-images h4 { margin: 0 0 10px; font-size: 14px; color: #303133; }
.image-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.detail-image-item { width: 140px; height: 140px; border-radius: 6px; }

.advice-loading { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 40px 0; color: #2f6fed; font-size: 15px; }
.advice-answer { max-height: 400px; overflow-y: auto; white-space: pre-wrap; line-height: 1.8; background: #f5f7fa; border-radius: 8px; padding: 16px; }
</style>
