<template>
  <div class="page inspection-page">
    <div class="page-header">
      <div>
        <h1>所有工单监控</h1>
        <p>管理电梯/扶梯点检工单，支持工单创建、状态流转、步骤结果填写和现场照片留痕。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">创建工单</el-button>
      </div>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" class="filter-form" label-width="80px">
        <el-form-item label="关键词">
          <el-input
            v-model.trim="queryForm.keyword"
            clearable
            placeholder="请输入工单编号/工单名称/设备名称"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="工单状态">
          <el-select v-model="queryForm.status" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in orderStatusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openCreateDialog">创建工单</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="orderList"
        row-key="id"
        border
        stripe
        class="inspection-table"
      >
        <el-table-column prop="order_no" label="工单编号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="order_name" label="工单名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="device_id" label="设备ID" width="90" />
        <el-table-column label="点检类型" min-width="110">
          <template #default="{ row }">
            {{ getInspectionTypeLabel(row.inspection_type) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.status)" effect="light">
              {{ getOrderStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to" label="指派人员" width="100">
          <template #default="{ row }">
            {{ displayValue(row.assigned_to) }}
          </template>
        </el-table-column>
        <el-table-column label="开始时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column label="完成时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetailDrawer(row)">查看详情</el-button>
            <el-button v-if="row.status === 'pending'" link type="primary" @click="handleStart(row)">
              开始
            </el-button>
            <el-button v-if="row.status === 'in_progress'" link type="primary" @click="openDetailDrawer(row)">
              填写步骤
            </el-button>
            <el-button v-if="row.status === 'in_progress'" link type="success" @click="handleComplete(row)">
              完成工单
            </el-button>
            <el-button v-if="canDeleteOrder" link type="danger" @click="handleDelete(row)">
              删除
            </el-button>
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
      v-model="createDialogVisible"
      title="创建点检工单"
      width="650px"
      destroy-on-close
      @closed="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
        class="create-form"
      >
        <el-form-item label="设备" prop="device_id">
          <el-select
            v-model="createForm.device_id"
            filterable
            placeholder="请选择设备"
            :loading="optionLoading"
          >
            <el-option
              v-for="device in deviceOptions"
              :key="device.id"
              :label="formatDeviceOption(device)"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="点检模板" prop="template_id">
          <el-select
            v-model="createForm.template_id"
            filterable
            placeholder="请选择点检模板"
            :loading="optionLoading"
          >
            <el-option
              v-for="template in templateOptions"
              :key="template.id"
              :label="template.template_name"
              :value="template.id"
            >
              <span>{{ template.template_name }}</span>
              <small class="option-extra">{{ getInspectionTypeLabel(template.inspection_type) }}</small>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="工单名称" prop="order_name">
          <el-input v-model.trim="createForm.order_name" placeholder="请输入工单名称" />
        </el-form-item>
        <el-form-item label="指派工人" prop="assigned_to">
          <el-select
            v-model="createForm.assigned_to"
            filterable
            placeholder="请选择维修工人"
            :loading="optionLoading"
          >
            <el-option
              v-for="worker in workerOptions"
              :key="worker.id"
              :label="worker.real_name ? `${worker.real_name}（${worker.username}）` : worker.username"
              :value="worker.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model.trim="createForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreateOrder">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-drawer
      v-model="detailDrawerVisible"
      title="工单详情"
      size="60%"
      class="order-drawer"
      destroy-on-close
    >
      <div v-loading="detailLoading" class="detail-content">
        <template v-if="detailData">
          <el-descriptions :column="2" border class="order-descriptions">
            <el-descriptions-item label="工单编号">{{ displayValue(detailData.order_no) }}</el-descriptions-item>
            <el-descriptions-item label="工单名称">{{ displayValue(detailData.order_name) }}</el-descriptions-item>
            <el-descriptions-item label="点检类型">{{ getInspectionTypeLabel(detailData.inspection_type) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getOrderStatusType(detailData.status)" effect="light">
                {{ getOrderStatusLabel(detailData.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="设备ID">{{ displayValue(detailData.device_id) }}</el-descriptions-item>
            <el-descriptions-item label="指派人员">{{ displayValue(detailData.assigned_to) }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatDate(detailData.started_at) }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ formatDate(detailData.completed_at) }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ displayValue(detailData.remark) }}</el-descriptions-item>
          </el-descriptions>

          <div class="steps-section">
            <div class="section-title">
              <span>点检步骤</span>
              <small>{{ stepList.length }} 项</small>
            </div>

            <el-empty v-if="stepList.length === 0" description="暂无点检步骤" />
            <el-table v-else :data="stepList" border stripe row-key="id" class="steps-table">
              <el-table-column prop="step_order" label="序号" width="70" />
              <el-table-column prop="area" label="区域" width="110" show-overflow-tooltip />
              <el-table-column prop="item_name" label="检查项目" min-width="140" show-overflow-tooltip />
              <el-table-column prop="item_content" label="检查内容" min-width="180" show-overflow-tooltip />
              <el-table-column prop="standard" label="检查标准" min-width="160" show-overflow-tooltip />
              <el-table-column label="结果" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStepResultType(row.result)" effect="light">
                    {{ getStepResultLabel(row.result) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ displayValue(row.remark) }}
                </template>
              </el-table-column>
              <el-table-column label="照片" width="100">
                <template #default="{ row }">
                  <el-button
                    v-if="row.photo_path"
                    link
                    type="primary"
                    @click="previewPhoto(row.photo_path)"
                  >
                    查看照片
                  </el-button>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column prop="checked_by" label="检查人" width="90">
                <template #default="{ row }">
                  {{ displayValue(row.checked_by) }}
                </template>
              </el-table-column>
              <el-table-column label="检查时间" min-width="170">
                <template #default="{ row }">
                  {{ formatDate(row.checked_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" fixed="right" width="110">
                <template #default="{ row }">
                  <el-button
                    link
                    type="primary"
                    :disabled="detailData.status === 'completed' || detailData.status === 'cancelled'"
                    @click="openStepDialog(row)"
                  >
                    填写结果
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </div>
    </el-drawer>

    <el-dialog
      v-model="stepDialogVisible"
      title="填写点检步骤结果"
      width="560px"
      destroy-on-close
      @closed="resetStepForm"
    >
      <div v-if="currentStep" class="step-summary">
        <strong>{{ currentStep.step_order }}. {{ currentStep.item_name }}</strong>
        <span>{{ currentStep.area }} / {{ currentStep.item_content }}</span>
      </div>
      <el-form :model="stepForm" label-width="90px" class="step-form">
        <el-form-item label="检查结果" required>
          <el-select v-model="stepForm.result" placeholder="请选择检查结果">
            <el-option label="正常" value="normal" />
            <el-option label="异常" value="abnormal" />
            <el-option label="不适用" value="not_applicable" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查备注">
          <el-input
            v-model.trim="stepForm.remark"
            type="textarea"
            :rows="4"
            placeholder="请输入检查备注"
          />
        </el-form-item>
        <el-form-item label="上传照片">
          <el-upload
            ref="stepUploadRef"
            v-model:file-list="stepFileList"
            class="step-upload"
            :auto-upload="false"
            :limit="1"
            accept=".jpg,.jpeg,.png,.webp"
            :on-change="handleStepFileChange"
            :on-remove="handleStepFileRemove"
            :on-exceed="handleStepFileExceed"
          >
            <el-button type="primary" plain>选择照片</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 jpg、jpeg、png、webp 图片。</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stepDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="stepSaving" @click="handleSaveStep">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="photoDialogVisible" title="点检照片预览" width="720px" @closed="releasePhotoUrl">
      <div v-loading="photoLoading" class="photo-preview">
        <el-image
          v-if="photoPreviewUrl"
          :src="photoPreviewUrl"
          fit="contain"
          :preview-src-list="[photoPreviewUrl]"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../../stores/user'
import { getDeviceList } from '../../api/devices'
import { getWorkers } from '../../api/users'
import { fetchFileBlob } from '../../api/files'
import {
  completeInspectionOrder,
  createInspectionOrder,
  deleteInspectionOrder,
  getInspectionOrderDetail,
  getInspectionOrders,
  getInspectionTemplates,
  startInspectionOrder,
  updateInspectionStep,
  uploadInspectionStepPhoto
} from '../../api/inspections'

const userStore = useUserStore()

const orderStatusOptions = [
  { label: '待开始', value: 'pending', type: 'warning' },
  { label: '进行中', value: 'in_progress', type: 'primary' },
  { label: '已完成', value: 'completed', type: 'success' },
  { label: '已取消', value: 'cancelled', type: 'info' }
]

const inspectionTypeOptions = [
  { label: '日常点检', value: 'daily' },
  { label: '月度点检', value: 'monthly' },
  { label: '季度点检', value: 'quarterly' },
  { label: '年度点检', value: 'annual' },
  { label: '故障专项', value: 'fault' }
]

const stepResultOptions = [
  { label: '未检查', value: 'unchecked', type: 'warning' },
  { label: '正常', value: 'normal', type: 'success' },
  { label: '异常', value: 'abnormal', type: 'danger' },
  { label: '不适用', value: 'not_applicable', type: 'info' }
]

const allowedImageExtensions = ['jpg', 'jpeg', 'png', 'webp']

const queryForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loading = ref(false)
const orderList = ref([])
const createDialogVisible = ref(false)
const createLoading = ref(false)
const optionLoading = ref(false)
const createFormRef = ref(null)
const deviceOptions = ref([])
const templateOptions = ref([])
const workerOptions = ref([])
const detailDrawerVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
const stepDialogVisible = ref(false)
const stepSaving = ref(false)
const currentStep = ref(null)
const stepUploadRef = ref(null)
const stepFileList = ref([])
const selectedStepFile = ref(null)
const photoDialogVisible = ref(false)
const photoLoading = ref(false)
const photoPreviewUrl = ref('')

const createForm = reactive(defaultCreateForm())

const createRules = {
  device_id: [{ required: true, message: '请选择设备', trigger: 'change' }],
  template_id: [{ required: true, message: '请选择点检模板', trigger: 'change' }],
  order_name: [{ required: true, message: '请输入工单名称', trigger: 'blur' }],
  assigned_to: [{ required: true, message: '请选择维修工人', trigger: 'change' }]
}

const stepForm = reactive({
  result: 'normal',
  remark: ''
})

const stepList = computed(() => detailData.value?.steps || [])
const currentUserId = computed(() => userStore.userInfo?.id || null)
const currentRole = computed(() => userStore.userInfo?.role || '')
const canDeleteOrder = computed(() => ['admin', 'auditor'].includes(currentRole.value))

function defaultCreateForm() {
  return {
    device_id: null,
    template_id: null,
    order_name: '',
    assigned_to: null,
    remark: ''
  }
}

function resetCreateForm() {
  Object.assign(createForm, defaultCreateForm())
  createFormRef.value?.clearValidate()
}

function displayValue(value) {
  return value === 0 ? 0 : value || '—'
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function getOptionItem(options, value) {
  return options.find((item) => item.value === value)
}

function getOrderStatusLabel(value) {
  return getOptionItem(orderStatusOptions, value)?.label || value || '—'
}

function getOrderStatusType(value) {
  return getOptionItem(orderStatusOptions, value)?.type || 'info'
}

function getInspectionTypeLabel(value) {
  return getOptionItem(inspectionTypeOptions, value)?.label || value || '—'
}

function getStepResultLabel(value) {
  return getOptionItem(stepResultOptions, value)?.label || value || '—'
}

function getStepResultType(value) {
  return getOptionItem(stepResultOptions, value)?.type || 'info'
}

function formatDeviceOption(device) {
  const code = device.device_code ? `（${device.device_code}）` : ''
  return `${device.device_name || `设备${device.id}`}${code}`
}

function getFileExtension(filename = '') {
  return filename.split('.').pop()?.toLowerCase() || ''
}

function isAllowedImage(file) {
  const extension = getFileExtension(file?.name || '')
  return allowedImageExtensions.includes(extension)
}

async function fetchOrderList() {
  loading.value = true
  try {
    const data = await getInspectionOrders({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: queryForm.keyword,
      status: queryForm.status
    })
    orderList.value = data?.items || []
    pagination.total = data?.total || 0
    pagination.page = data?.page || pagination.page
    pagination.page_size = data?.page_size || pagination.page_size
  } catch (error) {
    orderList.value = []
  } finally {
    loading.value = false
  }
}

async function loadCreateOptions() {
  optionLoading.value = true
  try {
    const [deviceData, templateData, workerData] = await Promise.all([
      getDeviceList({ page: 1, page_size: 100 }),
      getInspectionTemplates({ page: 1, page_size: 100, is_active: true }),
      getWorkers()
    ])
    deviceOptions.value = deviceData?.items || []
    templateOptions.value = templateData?.items || []
    workerOptions.value = workerData?.data || workerData || []
  } catch (error) {
    deviceOptions.value = []
    templateOptions.value = []
    workerOptions.value = []
  } finally {
    optionLoading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchOrderList()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.status = ''
  pagination.page = 1
  fetchOrderList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchOrderList()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchOrderList()
}

async function openCreateDialog() {
  resetCreateForm()
  createDialogVisible.value = true
  await loadCreateOptions()
}

async function handleCreateOrder() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return

  createLoading.value = true
  try {
    await createInspectionOrder({
      device_id: createForm.device_id,
      template_id: createForm.template_id,
      order_name: createForm.order_name,
      assigned_to: createForm.assigned_to || currentUserId.value,
      remark: createForm.remark
    })
    ElMessage.success('点检工单创建成功')
    createDialogVisible.value = false
    pagination.page = 1
    await fetchOrderList()
  } catch (error) {
    // request.js already shows backend errors.
  } finally {
    createLoading.value = false
  }
}

async function openDetailDrawer(row) {
  detailDrawerVisible.value = true
  await fetchOrderDetail(row.id)
}

async function fetchOrderDetail(orderId = detailData.value?.id) {
  if (!orderId) return
  detailLoading.value = true
  try {
    detailData.value = await getInspectionOrderDetail(orderId)
  } catch (error) {
    detailData.value = null
    ElMessage.error('获取工单详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function handleStart(row) {
  try {
    await startInspectionOrder(row.id)
    ElMessage.success('工单已开始')
    await fetchOrderList()
    if (detailData.value?.id === row.id) {
      await fetchOrderDetail(row.id)
    }
  } catch (error) {
    // request.js already shows backend errors.
  }
}

async function handleComplete(row) {
  try {
    await ElMessageBox.confirm(
      `确认完成工单"${row.order_name || row.order_no}"吗？`,
      '完成确认',
      {
        confirmButtonText: '确认完成',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await completeInspectionOrder(row.id)
    ElMessage.success('工单已完成')
    await fetchOrderList()
    if (detailData.value?.id === row.id) {
      await fetchOrderDetail(row.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      // request.js already shows backend errors.
    }
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除工单"${row.order_name || row.order_no}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteInspectionOrder(row.id)
    ElMessage.success('工单删除成功')
    if (orderList.value.length === 1 && pagination.page > 1) {
      pagination.page -= 1
    }
    await fetchOrderList()
    if (detailData.value?.id === row.id) {
      detailDrawerVisible.value = false
      detailData.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      // request.js already shows backend errors.
    }
  }
}

function openStepDialog(step) {
  currentStep.value = step
  stepForm.result = step.result === 'unchecked' ? 'normal' : step.result || 'normal'
  stepForm.remark = step.remark || ''
  selectedStepFile.value = null
  stepFileList.value = []
  stepDialogVisible.value = true
}

function resetStepForm() {
  currentStep.value = null
  stepForm.result = 'normal'
  stepForm.remark = ''
  selectedStepFile.value = null
  stepFileList.value = []
  stepUploadRef.value?.clearFiles()
}

function handleStepFileChange(file, fileList) {
  if (!isAllowedImage(file)) {
    ElMessage.warning('仅支持 jpg、jpeg、png、webp 图片')
    stepFileList.value = []
    selectedStepFile.value = null
    return
  }
  const latestFile = fileList[fileList.length - 1]
  stepFileList.value = latestFile ? [latestFile] : []
  selectedStepFile.value = latestFile || file
}

function handleStepFileRemove() {
  selectedStepFile.value = null
  stepFileList.value = []
}

function handleStepFileExceed(files) {
  const latestFile = files[0]
  if (!latestFile || !isAllowedImage(latestFile)) {
    ElMessage.warning('仅支持 jpg、jpeg、png、webp 图片')
    return
  }
  stepUploadRef.value?.clearFiles()
  stepFileList.value = []
  selectedStepFile.value = null
  stepUploadRef.value?.handleStart(latestFile)
}

async function handleSaveStep() {
  if (!currentStep.value || !detailData.value) return
  if (!stepForm.result) {
    ElMessage.warning('请选择检查结果')
    return
  }

  stepSaving.value = true
  try {
    let photoPath = currentStep.value.photo_path || ''
    const rawFile = selectedStepFile.value?.raw
    if (rawFile) {
      if (!isAllowedImage(rawFile)) {
        ElMessage.warning('仅支持 jpg、jpeg、png、webp 图片')
        return
      }
      const formData = new FormData()
      formData.append('file', rawFile)
      const uploadData = await uploadInspectionStepPhoto(detailData.value.id, currentStep.value.id, formData)
      photoPath = uploadData?.photo_path || photoPath
    }

    await updateInspectionStep(detailData.value.id, currentStep.value.id, {
      result: stepForm.result,
      remark: stepForm.remark,
      photo_path: photoPath
    })
    ElMessage.success('点检步骤已保存')
    stepDialogVisible.value = false
    await fetchOrderDetail(detailData.value.id)
    await fetchOrderList()
  } catch (error) {
    // request.js already shows backend errors.
  } finally {
    stepSaving.value = false
  }
}

async function previewPhoto(path) {
  releasePhotoUrl()
  photoDialogVisible.value = true
  photoLoading.value = true
  try {
    const blob = await fetchFileBlob(path)
    photoPreviewUrl.value = URL.createObjectURL(blob)
  } catch (error) {
    ElMessage.error(error.message || '照片预览失败')
    photoDialogVisible.value = false
  } finally {
    photoLoading.value = false
  }
}

function releasePhotoUrl() {
  if (photoPreviewUrl.value) {
    URL.revokeObjectURL(photoPreviewUrl.value)
    photoPreviewUrl.value = ''
  }
}

onMounted(() => {
  fetchOrderList()
})

onBeforeUnmount(() => {
  releasePhotoUrl()
})
</script>

<style scoped>
.inspection-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
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

.inspection-table {
  width: 100%;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.create-form :deep(.el-select) {
  width: 100%;
}

.option-extra {
  color: #8592a6;
  float: right;
  font-size: 12px;
  margin-left: 18px;
}

.detail-content {
  min-height: 360px;
}

.order-descriptions {
  margin-bottom: 22px;
}

.steps-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #17233d;
  font-weight: 700;
}

.section-title small {
  color: #7a869a;
  font-weight: 400;
}

.steps-table {
  width: 100%;
}

.step-summary {
  background: #f5f8fe;
  border: 1px solid #e5edf9;
  border-radius: 10px;
  color: #263955;
  display: flex;
  flex-direction: column;
  gap: 6px;
  line-height: 1.6;
  margin-bottom: 18px;
  padding: 12px;
}

.step-summary span {
  color: #66758d;
  font-size: 13px;
}

.step-form :deep(.el-select) {
  width: 100%;
}

.step-upload {
  width: 100%;
}

.photo-preview {
  align-items: center;
  display: flex;
  justify-content: center;
  min-height: 360px;
}

.photo-preview :deep(.el-image) {
  max-height: 68vh;
  max-width: 100%;
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
