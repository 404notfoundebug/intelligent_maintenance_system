<template>
  <div class="repair-cases-page">
    <div class="page-header">
      <div>
        <h1>故障案例审核入库</h1>
        <p>案例提交、审核与知识库入库管理</p>
      </div>
      <el-button type="primary" @click="openCreate">新建案例</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="案例标题/故障描述" clearable style="width:220px" @keyup.enter="handleSearch" />
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

    <!-- 案例列表 -->
    <el-table :data="cases" v-loading="loading" stripe border style="width:100%;margin-top:16px">
      <el-table-column prop="case_no" label="编号" width="140" />
      <el-table-column prop="title" label="案例标题" min-width="160" show-overflow-tooltip />
      <el-table-column prop="device_name" label="设备名称" width="140" show-overflow-tooltip />
      <el-table-column prop="fault_description" label="故障描述" min-width="180" show-overflow-tooltip />
      <el-table-column prop="status" label="审核状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.status]?.type || 'info'" size="small">
            {{ statusMap[row.status]?.label || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="submitted_by" label="提交人" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">详情</el-button>
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="success"
            @click="openAudit(row, 'approved')"
          >通过</el-button>
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="danger"
            @click="openAudit(row, 'rejected')"
          >驳回</el-button>
          <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
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
        @size-change="fetchCases"
        @current-change="fetchCases"
      />
    </div>

    <!-- 新建/编辑 Dialog -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑案例' : '新建案例'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="案例标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入案例标题" maxlength="200" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="device_name">
              <el-input v-model="form.device_name" placeholder="请输入设备名称" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="设备类型">
              <el-input v-model="form.device_type" placeholder="如 曳引电梯" maxlength="64" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联故障编号">
              <el-input v-model="form.fault_report_id" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="故障描述" prop="fault_description">
          <el-input v-model="form.fault_description" type="textarea" :rows="3" maxlength="1000" show-word-limit placeholder="请描述故障现象" />
        </el-form-item>
        <el-form-item label="故障原因" prop="fault_reason">
          <el-input v-model="form.fault_reason" type="textarea" :rows="3" maxlength="1000" show-word-limit placeholder="请分析故障原因" />
        </el-form-item>
        <el-form-item label="维修过程">
          <el-input v-model="form.repair_process" type="textarea" :rows="3" maxlength="2000" show-word-limit placeholder="请描述维修过程" />
        </el-form-item>
        <el-form-item label="维修结果">
          <el-input v-model="form.repair_result" type="textarea" :rows="2" maxlength="1000" show-word-limit placeholder="维修结果" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="使用工具">
              <el-input v-model="form.tools_used" placeholder="如 万用表、扳手" maxlength="500" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全注意事项">
              <el-input v-model="form.safety_notes" placeholder="安全注意事项" maxlength="500" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情 Dialog -->
    <el-dialog v-model="detailVisible" title="案例详情" width="750px">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="案例编号">{{ detail.case_no }}</el-descriptions-item>
          <el-descriptions-item label="审核状态">
            <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="案例标题">{{ detail.title }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ detail.device_name }}</el-descriptions-item>
          <el-descriptions-item label="设备类型">{{ detail.device_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="关联故障编号">{{ detail.fault_report_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障描述" :span="2">{{ detail.fault_description }}</el-descriptions-item>
          <el-descriptions-item label="故障原因" :span="2">{{ detail.fault_reason || '-' }}</el-descriptions-item>
          <el-descriptions-item label="维修过程" :span="2">{{ detail.repair_process || '-' }}</el-descriptions-item>
          <el-descriptions-item label="维修结果" :span="2">{{ detail.repair_result || '-' }}</el-descriptions-item>
          <el-descriptions-item label="使用工具">{{ detail.tools_used || '-' }}</el-descriptions-item>
          <el-descriptions-item label="安全事项">{{ detail.safety_notes || '-' }}</el-descriptions-item>
          <el-descriptions-item label="提交人">{{ detail.submitted_by }}</el-descriptions-item>
          <el-descriptions-item label="审核人">{{ detail.reviewed_by || '-' }}</el-descriptions-item>
          <el-descriptions-item label="审核意见" :span="2">{{ detail.review_comment || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="审核时间">{{ formatTime(detail.reviewed_at) }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detail.audit_records?.length" class="audit-section">
          <h4>审核记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="record in detail.audit_records"
              :key="record.id"
              :timestamp="formatTime(record.created_at)"
              placement="top"
            >
              <el-tag :type="record.action === 'approved' ? 'success' : 'danger'" size="small">
                {{ record.action === 'approved' ? '通过' : '驳回' }}
              </el-tag>
              <span style="margin-left:8px">{{ record.comment || '无备注' }}</span>
              <div style="font-size:12px;color:#909399">审核人：{{ record.reviewed_by }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </template>
    </el-dialog>

    <!-- 审核 Dialog -->
    <el-dialog v-model="auditVisible" title="案例审核" width="480px" :close-on-click-modal="false">
      <el-form ref="auditFormRef" :model="auditForm" label-position="top">
        <el-form-item :label="auditForm.action === 'approved' ? '审核通过备注' : '驳回理由'" prop="comment">
          <el-input v-model="auditForm.comment" type="textarea" :rows="4" :placeholder="auditForm.action === 'approved' ? '可选，填写审核意见' : '请填写驳回理由'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditVisible = false">取消</el-button>
        <el-button :type="auditForm.action === 'approved' ? 'success' : 'danger'" :loading="auditSaving" @click="handleAudit">
          {{ auditForm.action === 'approved' ? '审核通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRepairCases, getRepairCaseDetail, createRepairCase, updateRepairCase, auditRepairCase, deleteRepairCase } from '@/api/cases'

const statusOptions = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' }
]

const statusMap = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' }
}

const cases = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const searchForm = reactive({ keyword: '', status: '' })

// 新建/编辑
const formVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  title: '',
  device_name: '',
  device_type: '',
  fault_report_id: '',
  fault_description: '',
  fault_reason: '',
  repair_process: '',
  repair_result: '',
  tools_used: '',
  safety_notes: ''
})

const formRules = {
  title: [{ required: true, message: '请输入案例标题', trigger: 'blur' }],
  device_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  fault_description: [{ required: true, message: '请输入故障描述', trigger: 'blur' }],
  fault_reason: [{ required: true, message: '请输入故障原因', trigger: 'blur' }]
}

// 详情
const detailVisible = ref(false)
const detail = ref(null)

// 审核
const auditVisible = ref(false)
const auditSaving = ref(false)
const auditFormRef = ref(null)
const auditingCaseId = ref(null)
const auditForm = reactive({ action: '', comment: '' })

function formatTime(str) {
  if (!str) return '-'
  return new Date(str).toLocaleString('zh-CN')
}

async function fetchCases() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.status) params.status = searchForm.status
    const res = await getRepairCases(params)
    cases.value = res.items || []
    pagination.total = res.total || 0
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '获取案例列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() { pagination.page = 1; fetchCases() }
function handleReset() { searchForm.keyword = ''; searchForm.status = ''; pagination.page = 1; fetchCases() }

function openCreate() {
  isEdit.value = false
  editingId.value = null
  Object.keys(form).forEach(k => form[k] = '')
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  form.title = row.title || ''
  form.device_name = row.device_name || ''
  form.device_type = row.device_type || ''
  form.fault_report_id = row.fault_report_id || ''
  form.fault_description = row.fault_description || ''
  form.fault_reason = row.fault_reason || ''
  form.repair_process = row.repair_process || ''
  form.repair_result = row.repair_result || ''
  form.tools_used = row.tools_used || ''
  form.safety_notes = row.safety_notes || ''
  formVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      title: form.title,
      device_name: form.device_name,
      device_type: form.device_type || undefined,
      fault_report_id: form.fault_report_id ? Number(form.fault_report_id) : undefined,
      fault_description: form.fault_description,
      fault_reason: form.fault_reason,
      repair_process: form.repair_process || undefined,
      repair_result: form.repair_result || undefined,
      tools_used: form.tools_used || undefined,
      safety_notes: form.safety_notes || undefined
    }
    if (isEdit.value) {
      await updateRepairCase(editingId.value, payload)
      ElMessage.success('案例更新成功')
    } else {
      await createRepairCase(payload)
      ElMessage.success('案例创建成功，等待审核')
    }
    formVisible.value = false
    fetchCases()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function openDetail(row) {
  try {
    const res = await getRepairCaseDetail(row.id)
    detail.value = res || row
    detailVisible.value = true
  } catch (err) {
    ElMessage.error('获取案例详情失败')
  }
}

function openAudit(row, action) {
  auditingCaseId.value = row.id
  auditForm.action = action
  auditForm.comment = ''
  auditVisible.value = true
}

async function handleAudit() {
  auditSaving.value = true
  try {
    await auditRepairCase(auditingCaseId.value, {
      action: auditForm.action,
      comment: auditForm.comment || undefined
    })
    ElMessage.success(auditForm.action === 'approved' ? '审核通过' : '已驳回')
    auditVisible.value = false
    fetchCases()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.response?.data?.detail || '审核失败')
  } finally {
    auditSaving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除案例「${row.case_no}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await deleteRepairCase(row.id)
    ElMessage.success('删除成功')
    fetchCases()
  } catch (err) {
    if (err !== 'cancel' && err?.response) {
      ElMessage.error(err?.response?.data?.message || '删除失败')
    }
  }
}

onMounted(fetchCases)
</script>

<style scoped>
.repair-cases-page { padding: 0; }

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

.audit-section { margin-top: 20px; }
.audit-section h4 { margin: 0 0 12px; font-size: 14px; color: #303133; }
</style>
