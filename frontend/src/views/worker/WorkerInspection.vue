<template>
  <div class="worker-inspection-page">
    <!-- 工单列表卡片 -->
    <el-card class="list-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>点检工单执行</span>
          <el-tag type="info" effect="plain" size="small">{{ orders.length }} 个工单</el-tag>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="orders"
        stripe
        row-key="id"
        empty-text="暂未分配工单"
      >
        <el-table-column prop="order_no" label="工单编号" min-width="170" show-overflow-tooltip />
        <el-table-column prop="order_name" label="工单名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="点检类型" width="100">
          <template #default="{ row }">{{ typeLabel(row.inspection_type) }}</template>
        </el-table-column>
        <el-table-column label="设备" width="80">
          <template #default="{ row }">#{{ row.device_id }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="240">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="primary"
              @click="handleStart(row)"
            >
              开始执行
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              size="small"
              type="primary"
              @click="openExecute(row)"
            >
              填写步骤
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              size="small"
              type="success"
              :disabled="!allStepsDone(row)"
              @click="handleComplete(row)"
            >
              完成工单
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              size="small"
              type="info"
              plain
              @click="openExecute(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 工单执行抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="currentOrder ? `工单：${currentOrder.order_name || currentOrder.order_no}` : ''"
      size="65%"
      destroy-on-close
      @closed="resetDrawer"
    >
      <div v-loading="detailLoading" class="drawer-content">
        <!-- 工单基本信息 -->
        <el-descriptions v-if="currentOrder" :column="2" border size="small" class="order-info">
          <el-descriptions-item label="工单编号">{{ currentOrder.order_no || '-' }}</el-descriptions-item>
          <el-descriptions-item label="点检类型">{{ typeLabel(currentOrder.inspection_type) }}</el-descriptions-item>
          <el-descriptions-item label="设备ID">{{ currentOrder.device_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentOrder.status)" effect="light" size="small">
              {{ statusLabel(currentOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 步骤列表 -->
        <div class="steps-section">
          <div class="section-title">
            <span>点检步骤</span>
            <small>{{ steps.length }} 项（已填 {{ filledCount }} / {{ steps.length }}）</small>
          </div>

          <el-empty v-if="steps.length === 0" description="暂无点检步骤" />
          <div v-else class="step-list">
            <div
              v-for="step in steps"
              :key="step.id"
              class="step-item"
              :class="{ 'step-filled': step.result && step.result !== 'unchecked' }"
            >
              <div class="step-header">
                <span class="step-order">{{ step.step_order }}</span>
                <div class="step-info">
                  <strong>{{ step.item_name }}</strong>
                  <span class="step-area">{{ step.area }}</span>
                </div>
                <el-tag
                  :type="stepResultType(step.result)"
                  effect="light"
                  size="small"
                  class="step-result-tag"
                >
                  {{ stepResultLabel(step.result) }}
                </el-tag>
              </div>

              <div class="step-body">
                <div class="step-detail">
                  <p><label>检查内容：</label>{{ step.item_content || '-' }}</p>
                  <p><label>检查标准：</label>{{ step.standard || '-' }}</p>
                </div>

                <!-- 执行表单（仅在 in_progress 状态可编辑） -->
                <template v-if="isEditable">
                  <div class="step-form">
                    <el-form label-width="80px" size="small">
                      <el-form-item label="检查结果">
                        <el-select v-model="stepFormData[step.id].result" placeholder="请选择">
                          <el-option label="正常" value="normal" />
                          <el-option label="异常" value="abnormal" />
                          <el-option label="不适用" value="not_applicable" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="备注">
                        <el-input
                          v-model="stepFormData[step.id].remark"
                          type="textarea"
                          :rows="2"
                          placeholder="请输入检查备注"
                        />
                      </el-form-item>
                      <el-form-item label="现场照片">
                        <div class="photo-area">
                          <div v-if="stepFormData[step.id].previewUrl" class="photo-preview-mini">
                            <img :src="stepFormData[step.id].previewUrl" alt="现场照片" />
                            <el-button
                              type="danger"
                              size="small"
                              circle
                              class="photo-remove"
                              @click="removePhoto(step.id)"
                            >
                              ×
                            </el-button>
                          </div>
                          <el-upload
                            v-else
                            :auto-upload="false"
                            :limit="1"
                            accept=".jpg,.jpeg,.png,.webp"
                            :on-change="(file) => handlePhotoChange(step.id, file)"
                          >
                            <el-button size="small" type="primary" plain>选择照片</el-button>
                          </el-upload>
                          <span v-if="step.photo_path && !stepFormData[step.id].previewUrl" class="existing-photo">
                            已有照片
                            <el-button link type="primary" size="small" @click="previewPhoto(step.photo_path)">
                              查看
                            </el-button>
                          </span>
                        </div>
                      </el-form-item>
                      <el-form-item>
                        <el-button
                          type="primary"
                          size="small"
                          :loading="stepSaving[step.id]"
                          @click="saveStep(step)"
                        >
                          保存此步骤
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </div>
                </template>

                <!-- 只读模式显示已保存结果 -->
                <template v-else-if="step.result && step.result !== 'unchecked'">
                  <div class="step-readonly">
                    <p v-if="step.remark"><label>备注：</label>{{ step.remark }}</p>
                    <p v-if="step.checked_at"><label>检查时间：</label>{{ fmt(step.checked_at) }}</p>
                    <div v-if="step.photo_path" class="photo-mini">
                      <el-button link type="primary" size="small" @click="previewPhoto(step.photo_path)">
                        查看现场照片
                      </el-button>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="drawerVisible = false">关闭</el-button>
        <el-button
          v-if="isEditable && currentOrder?.status === 'in_progress'"
          type="success"
          :disabled="!allStepsDone(currentOrder)"
          :loading="completing"
          @click="handleComplete(currentOrder)"
        >
          完成工单
        </el-button>
      </template>
    </el-drawer>

    <!-- 照片预览弹窗 -->
    <el-dialog v-model="photoVisible" title="现场照片" width="720px" @closed="releasePhoto">
      <div v-loading="photoLoading" class="photo-full">
        <el-image v-if="photoUrl" :src="photoUrl" fit="contain" :preview-src-list="[photoUrl]" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { fetchFileBlob } from '@/api/files'
import {
  getInspectionOrders,
  getInspectionOrderDetail,
  startInspectionOrder,
  completeInspectionOrder,
  updateInspectionStep,
  uploadInspectionStepPhoto
} from '@/api/inspections'

const userStore = useUserStore()

const orders = ref([])
const loading = ref(false)
const drawerVisible = ref(false)
const detailLoading = ref(false)
const currentOrder = ref(null)
const steps = ref([])
const completing = ref(false)

// 每步骤的表单数据 { stepId: { result, remark, previewUrl, file } }
const stepFormData = reactive({})
const stepSaving = reactive({})

// 照片预览
const photoVisible = ref(false)
const photoLoading = ref(false)
const photoUrl = ref('')

const allowedExts = ['jpg', 'jpeg', 'png', 'webp']

// 状态映射
const statusMap = {
  pending: { label: '待开始', type: 'warning' },
  in_progress: { label: '进行中', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'info' }
}
const typeMap = {
  daily: '日常点检',
  monthly: '月度点检',
  quarterly: '季度点检',
  annual: '年度点检',
  fault: '故障专项'
}
const resultMap = {
  unchecked: { label: '未检查', type: 'warning' },
  normal: { label: '正常', type: 'success' },
  abnormal: { label: '异常', type: 'danger' },
  not_applicable: { label: '不适用', type: 'info' }
}

function statusLabel(s) { return statusMap[s]?.label || s || '-' }
function statusType(s) { return statusMap[s]?.type || 'info' }
function typeLabel(t) { return typeMap[t] || t || '-' }
function stepResultLabel(r) { return resultMap[r]?.label || '未检查' }
function stepResultType(r) { return resultMap[r]?.type || 'warning' }
function fmt(v) { return v ? new Date(v).toLocaleString() : '-' }

const isEditable = computed(() =>
  currentOrder.value?.status === 'in_progress'
)

const filledCount = computed(() =>
  steps.value.filter(s => s.result && s.result !== 'unchecked').length
)

function allStepsDone(order) {
  if (!order?.steps?.length) return false
  return order.steps.every(s => s.result && s.result !== 'unchecked')
}

function getExt(filename) {
  return (filename || '').split('.').pop()?.toLowerCase() || ''
}

// ---- 工单列表 ----
async function fetchOrders() {
  loading.value = true
  try {
    const res = await getInspectionOrders({ page: 1, page_size: 100 })
    orders.value = res?.items || []
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrders)

// ---- 开始工单 ----
async function handleStart(row) {
  try {
    await startInspectionOrder(row.id)
    ElMessage.success('工单已开始')
    await fetchOrders()
  } catch {
    // error handled by interceptor
  }
}

// ---- 打开执行抽屉 ----
async function openExecute(row) {
  drawerVisible.value = true
  await loadOrderDetail(row.id)
}

async function loadOrderDetail(orderId) {
  detailLoading.value = true
  try {
    const data = await getInspectionOrderDetail(orderId)
    currentOrder.value = data
    steps.value = data?.steps || []
    initStepForms()
  } catch {
    ElMessage.error('加载工单详情失败')
    drawerVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function initStepForms() {
  for (const step of steps.value) {
    stepFormData[step.id] = {
      result: step.result === 'unchecked' ? 'normal' : (step.result || 'normal'),
      remark: step.remark || '',
      previewUrl: null,
      file: null
    }
    stepSaving[step.id] = false
  }
}

function resetDrawer() {
  currentOrder.value = null
  steps.value = []
  Object.keys(stepFormData).forEach(k => delete stepFormData[k])
  Object.keys(stepSaving).forEach(k => delete stepSaving[k])
}

// ---- 步骤操作 ----
function handlePhotoChange(stepId, uploadFile) {
  const ext = getExt(uploadFile?.name || '')
  if (!allowedExts.includes(ext)) {
    ElMessage.warning('仅支持 jpg、jpeg、png、webp 图片')
    return
  }
  const file = uploadFile.raw || uploadFile
  stepFormData[stepId].file = file
  stepFormData[stepId].previewUrl = URL.createObjectURL(file)
}

function removePhoto(stepId) {
  if (stepFormData[stepId].previewUrl) {
    URL.revokeObjectURL(stepFormData[stepId].previewUrl)
  }
  stepFormData[stepId].previewUrl = null
  stepFormData[stepId].file = null
}

async function saveStep(step) {
  if (!currentOrder.value) return
  const form = stepFormData[step.id]
  if (!form.result) {
    ElMessage.warning('请选择检查结果')
    return
  }

  stepSaving[step.id] = true
  try {
    let photoPath = step.photo_path || ''

    // 先上传照片（如有）
    if (form.file) {
      const fd = new FormData()
      fd.append('file', form.file)
      const uploadRes = await uploadInspectionStepPhoto(currentOrder.value.id, step.id, fd)
      photoPath = uploadRes?.photo_path || uploadRes?.data?.photo_path || photoPath
    }

    // 保存步骤结果
    await updateInspectionStep(currentOrder.value.id, step.id, {
      result: form.result,
      remark: form.remark,
      photo_path: photoPath
    })

    ElMessage.success(`步骤 ${step.step_order} 已保存`)
    // 更新本地数据
    step.result = form.result
    step.remark = form.remark
    step.photo_path = photoPath
    step.checked_at = new Date().toISOString()
    if (stepFormData[step.id].previewUrl) {
      URL.revokeObjectURL(stepFormData[step.id].previewUrl)
    }
    stepFormData[step.id].previewUrl = null
    stepFormData[step.id].file = null

    // 刷新工单列表
    await fetchOrders()
  } catch {
    // error handled by interceptor
  } finally {
    stepSaving[step.id] = false
  }
}

// ---- 完成工单 ----
async function handleComplete(row) {
  try {
    await ElMessageBox.confirm(
      `确认完成工单「${row.order_name || row.order_no}」吗？完成后不可修改步骤。`,
      '完成确认',
      { confirmButtonText: '确认完成', cancelButtonText: '取消', type: 'warning' }
    )
    await completeInspectionOrder(row.id)
    ElMessage.success('工单已完成')
    drawerVisible.value = false
    await fetchOrders()
  } catch (e) {
    if (e !== 'cancel') {
      // error handled by interceptor
    }
  }
}

// ---- 照片预览 ----
async function previewPhoto(path) {
  releasePhoto()
  photoVisible.value = true
  photoLoading.value = true
  try {
    const blob = await fetchFileBlob(path)
    photoUrl.value = URL.createObjectURL(blob)
  } catch {
    ElMessage.error('照片加载失败')
    photoVisible.value = false
  } finally {
    photoLoading.value = false
  }
}

function releasePhoto() {
  if (photoUrl.value) {
    URL.revokeObjectURL(photoUrl.value)
    photoUrl.value = ''
  }
}

onBeforeUnmount(() => {
  releasePhoto()
  Object.keys(stepFormData).forEach(k => {
    if (stepFormData[k]?.previewUrl) {
      URL.revokeObjectURL(stepFormData[k].previewUrl)
    }
  })
})
</script>

<style scoped>
.worker-inspection-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.list-card {
  border: 1px solid rgba(30, 92, 180, 0.08);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(16, 41, 84, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ---- 抽屉内容 ---- */
.drawer-content {
  min-height: 400px;
}

.order-info {
  margin-bottom: 24px;
}

.steps-section {
  margin-top: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #17233d;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-title small {
  color: #7a869a;
  font-weight: 400;
}

/* ---- 步骤卡片 ---- */
.step-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.step-item {
  border: 1px solid #e5edf9;
  border-radius: 12px;
  padding: 18px;
  background: #fafcfe;
  transition: border-color 0.2s;
}

.step-item.step-filled {
  border-color: #b7d6f5;
  background: #f5faff;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.step-order {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #e8f0fe;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.step-filled .step-order {
  background: #d1fae5;
  color: #059669;
}

.step-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-info strong {
  font-size: 0.95rem;
  color: #1e293b;
}

.step-area {
  font-size: 0.78rem;
  color: #94a3b8;
}

.step-body {
  padding-left: 44px;
}

.step-detail {
  margin-bottom: 12px;
}

.step-detail p {
  margin: 3px 0;
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.6;
}

.step-detail label {
  color: #64748b;
  font-weight: 500;
}

.step-form {
  border-top: 1px dashed #e2e8f0;
  padding-top: 12px;
  margin-top: 8px;
}

.step-form :deep(.el-select) {
  width: 100%;
}

.photo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.photo-preview-mini {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.photo-preview-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  font-size: 12px;
}

.existing-photo {
  font-size: 0.8rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.step-readonly {
  border-top: 1px dashed #e2e8f0;
  padding-top: 10px;
  margin-top: 6px;
}

.step-readonly p {
  margin: 2px 0;
  font-size: 0.85rem;
  color: #475569;
}

.step-readonly label {
  color: #64748b;
  font-weight: 500;
}

.photo-mini {
  margin-top: 6px;
}

.photo-full {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360px;
}

.photo-full :deep(.el-image) {
  max-height: 68vh;
  max-width: 100%;
}
</style>
