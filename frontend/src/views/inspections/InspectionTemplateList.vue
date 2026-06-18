<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>点检工单模板管理</h1>
        <p>管理点检模板，支持模板创建、编辑、删除和步骤查看。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/admin/inspection-templates/add')">
          新建模板
        </el-button>
      </div>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" class="filter-form" label-width="80px">
        <el-form-item label="关键词">
          <el-input
            v-model.trim="queryForm.keyword"
            clearable
            placeholder="请输入模板名称"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="queryForm.device_type" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option label="曳引电梯" value="traction_elevator" />
            <el-option label="液压电梯" value="hydraulic_elevator" />
            <el-option label="自动扶梯" value="escalator" />
            <el-option label="自动人行道" value="moving_walkway" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.is_active" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="templateList"
        row-key="id"
        border
        stripe
      >
        <el-table-column prop="template_name" label="模板名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="设备类型" width="120">
          <template #default="{ row }">
            {{ getDeviceTypeLabel(row.device_type) }}
          </template>
        </el-table-column>
        <el-table-column label="点检类型" width="110">
          <template #default="{ row }">
            {{ getInspectionTypeLabel(row.inspection_type) }}
          </template>
        </el-table-column>
        <el-table-column label="步骤数" width="90" align="center">
          <template #default="{ row }">
            {{ row.steps?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="240">
          <template #default="{ row }">
            <el-button link type="primary" @click="openStepDrawer(row)">查看步骤</el-button>
            <el-button link type="primary" @click="$router.push(`/admin/inspection-templates/edit/${row.id}`)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 步骤详情抽屉 -->
    <el-drawer
      v-model="stepDrawerVisible"
      :title="`模板步骤 — ${currentTemplate?.template_name || ''}`"
      size="50%"
      destroy-on-close
    >
      <div v-loading="stepLoading" class="step-drawer-content">
        <template v-if="currentTemplateSteps.length">
          <div v-for="(step, idx) in currentTemplateSteps" :key="step.id || idx" class="step-card">
            <div class="step-card-header">
              <span class="step-order">步骤 {{ step.step_order }}</span>
              <div class="step-tags">
                <el-tag v-if="step.required_photo" type="warning" size="small">需拍照</el-tag>
                <el-tag v-if="step.required_remark" type="info" size="small">需备注</el-tag>
              </div>
            </div>
            <div class="step-card-body">
              <div class="step-field"><span class="step-label">区域</span>{{ step.area }}</div>
              <div class="step-field"><span class="step-label">项目</span>{{ step.item_name }}</div>
              <div class="step-field"><span class="step-label">内容</span>{{ step.item_content }}</div>
              <div class="step-field"><span class="step-label">标准</span>{{ step.standard || '—' }}</div>
            </div>
          </div>
        </template>
        <el-empty v-else description="暂无步骤" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getInspectionTemplates,
  deleteInspectionTemplate
} from '../../api/inspections'

const deviceTypeOptions = [
  { label: '曳引电梯', value: 'traction_elevator' },
  { label: '液压电梯', value: 'hydraulic_elevator' },
  { label: '自动扶梯', value: 'escalator' },
  { label: '自动人行道', value: 'moving_walkway' }
]

const inspectionTypeOptions = [
  { label: '日常点检', value: 'daily' },
  { label: '月度点检', value: 'monthly' },
  { label: '季度点检', value: 'quarterly' },
  { label: '年度点检', value: 'annual' },
  { label: '故障专项', value: 'fault' }
]

const queryForm = reactive({
  keyword: '',
  device_type: '',
  is_active: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loading = ref(false)
const templateList = ref([])

const stepDrawerVisible = ref(false)
const stepLoading = ref(false)
const currentTemplate = ref(null)
const currentTemplateSteps = ref([])

function getDeviceTypeLabel(value) {
  return deviceTypeOptions.find(i => i.value === value)?.label || value || '—'
}

function getInspectionTypeLabel(value) {
  return inspectionTypeOptions.find(i => i.value === value)?.label || value || '—'
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d.getTime())) return value
  return d.toLocaleString()
}

async function fetchTemplateList() {
  loading.value = true
  try {
    const data = await getInspectionTemplates({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: queryForm.keyword || undefined,
      device_type: queryForm.device_type || undefined,
      is_active: queryForm.is_active === '' ? undefined : queryForm.is_active
    })
    templateList.value = data?.items || []
    pagination.total = data?.total || 0
    pagination.page = data?.page || pagination.page
    pagination.page_size = data?.page_size || pagination.page_size
  } catch {
    templateList.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchTemplateList()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.device_type = ''
  queryForm.is_active = ''
  pagination.page = 1
  fetchTemplateList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchTemplateList()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchTemplateList()
}

async function openStepDrawer(row) {
  currentTemplate.value = row
  stepDrawerVisible.value = true
  stepLoading.value = true
  try {
    // 如果 row 已有 steps 则直接使用，否则重新拉取
    if (row.steps?.length) {
      currentTemplateSteps.value = row.steps
    } else {
      const data = await getInspectionTemplates({ page: 1, page_size: 1 })
      // 拉取单个模板详情
      const detail = await import('../../api/inspections').then(m =>
        m.getInspectionTemplateDetail(row.id)
      )
      currentTemplateSteps.value = detail?.steps || []
    }
  } catch {
    currentTemplateSteps.value = row.steps || []
  } finally {
    stepLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除模板"${row.template_name}"吗？`,
      '删除确认',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteInspectionTemplate(row.id)
    ElMessage.success('模板删除成功')
    if (templateList.value.length === 1 && pagination.page > 1) {
      pagination.page -= 1
    }
    await fetchTemplateList()
  } catch (e) {
    if (e !== 'cancel') {
      // request.js shows errors
    }
  }
}

onMounted(() => {
  fetchTemplateList()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.filter-card,
.table-card {
  border: 1px solid rgba(30, 92, 180, 0.08);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(16, 41, 84, 0.06);
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(180px, 240px) minmax(160px, 200px) auto;
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

/* 步骤抽屉 */
.step-drawer-content {
  min-height: 300px;
}

.step-card {
  border: 1px solid #e5edf9;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 12px;
  background: #f5f8fe;
}

.step-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-order {
  font-weight: 700;
  color: #17233d;
  font-size: 14px;
}

.step-tags {
  display: flex;
  gap: 6px;
}

.step-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step-field {
  font-size: 13px;
  color: #263955;
  line-height: 1.6;
}

.step-label {
  color: #8592a6;
  margin-right: 8px;
  font-size: 12px;
}

@media (max-width: 1180px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(200px, 1fr));
  }
}

@media (max-width: 760px) {
  .filter-form {
    grid-template-columns: 1fr;
  }
}
</style>
