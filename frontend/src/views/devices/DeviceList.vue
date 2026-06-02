<template>
  <div class="page device-page">
    <div class="page-header">
      <div>
        <h1>设备管理</h1>
        <p>统一维护电梯、扶梯和自动人行道设备台账，支撑故障上报、点检工单与维保记录关联。</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">新增设备</el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" class="filter-form" label-width="80px">
        <el-form-item label="关键词">
          <el-input
            v-model.trim="queryForm.keyword"
            clearable
            placeholder="请输入设备名称/编号/安装位置"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="queryForm.device_type" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in deviceTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openCreateDialog">新增设备</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="deviceList"
        row-key="id"
        border
        stripe
        class="device-table"
      >
        <el-table-column prop="device_code" label="设备编号" min-width="120" />
        <el-table-column prop="device_name" label="设备名称" min-width="140" />
        <el-table-column label="设备类型" min-width="120">
          <template #default="{ row }">
            {{ getDeviceTypeLabel(row.device_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="device_model" label="设备型号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="installation_location" label="安装位置" min-width="150" show-overflow-tooltip />
        <el-table-column prop="maintenance_company" label="维保单位" min-width="150" show-overflow-tooltip />
        <el-table-column prop="responsible_person" label="负责人" min-width="100" />
        <el-table-column prop="contact_phone" label="联系电话" min-width="130" />
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="190">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetailDialog(row)">查看</el-button>
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
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

    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑设备' : '新增设备'"
      width="680px"
      destroy-on-close
    >
      <el-form
        ref="deviceFormRef"
        :model="deviceForm"
        :rules="formRules"
        label-width="100px"
        class="device-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="设备名称" prop="device_name">
              <el-input v-model.trim="deviceForm.device_name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备编号" prop="device_code">
              <el-input v-model.trim="deviceForm.device_code" placeholder="请输入设备编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备类型" prop="device_type">
              <el-select v-model="deviceForm.device_type" placeholder="请选择设备类型">
                <el-option
                  v-for="item in deviceTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备型号">
              <el-input v-model.trim="deviceForm.device_model" placeholder="请输入设备型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产厂家">
              <el-input v-model.trim="deviceForm.manufacturer" placeholder="请输入生产厂家" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安装位置">
              <el-input v-model.trim="deviceForm.installation_location" placeholder="请输入安装位置" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="维保单位">
              <el-input v-model.trim="deviceForm.maintenance_company" placeholder="请输入维保单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人">
              <el-input v-model.trim="deviceForm.responsible_person" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model.trim="deviceForm.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态">
              <el-select v-model="deviceForm.status" placeholder="请选择设备状态">
                <el-option
                  v-for="item in statusOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model.trim="deviceForm.remark"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="设备详情" width="760px">
      <el-descriptions v-if="detailData" :column="2" border>
        <el-descriptions-item label="设备编号">{{ displayValue(detailData.device_code) }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ displayValue(detailData.device_name) }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ getDeviceTypeLabel(detailData.device_type) }}</el-descriptions-item>
        <el-descriptions-item label="设备型号">{{ displayValue(detailData.device_model) }}</el-descriptions-item>
        <el-descriptions-item label="生产厂家">{{ displayValue(detailData.manufacturer) }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ displayValue(detailData.installation_location) }}</el-descriptions-item>
        <el-descriptions-item label="维保单位">{{ displayValue(detailData.maintenance_company) }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ displayValue(detailData.responsible_person) }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ displayValue(detailData.contact_phone) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(detailData.status)" effect="light">
            {{ getStatusLabel(detailData.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(detailData.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ displayValue(detailData.remark) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createDevice,
  deleteDevice,
  getDeviceDetail,
  getDeviceList,
  updateDevice
} from '../../api/devices'

const deviceTypeOptions = [
  { label: '曳引电梯', value: 'traction_elevator' },
  { label: '液压电梯', value: 'hydraulic_elevator' },
  { label: '自动扶梯', value: 'escalator' },
  { label: '自动人行道', value: 'moving_walkway' }
]

const statusOptions = [
  { label: '正常', value: 'normal', type: 'success' },
  { label: '维保中', value: 'maintenance', type: 'primary' },
  { label: '故障', value: 'fault', type: 'danger' },
  { label: '停用', value: 'disabled', type: 'info' }
]

const queryForm = reactive({
  keyword: '',
  device_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loading = ref(false)
const submitLoading = ref(false)
const deviceList = ref([])
const formDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const currentDeviceId = ref(null)
const deviceFormRef = ref(null)
const detailData = ref(null)

const defaultForm = () => ({
  device_name: '',
  device_code: '',
  device_type: '',
  device_model: '',
  manufacturer: '',
  installation_location: '',
  maintenance_company: '',
  responsible_person: '',
  contact_phone: '',
  status: 'normal',
  remark: ''
})

const deviceForm = reactive(defaultForm())

const formRules = {
  device_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }]
}

function assignForm(data = {}) {
  Object.assign(deviceForm, defaultForm(), {
    device_name: data.device_name || '',
    device_code: data.device_code || '',
    device_type: data.device_type || '',
    device_model: data.device_model || '',
    manufacturer: data.manufacturer || '',
    installation_location: data.installation_location || '',
    maintenance_company: data.maintenance_company || '',
    responsible_person: data.responsible_person || '',
    contact_phone: data.contact_phone || '',
    status: data.status || 'normal',
    remark: data.remark || ''
  })
}

function getDeviceTypeLabel(value) {
  return deviceTypeOptions.find((item) => item.value === value)?.label || value || '-'
}

function getStatusItem(value) {
  return statusOptions.find((item) => item.value === value)
}

function getStatusLabel(value) {
  return getStatusItem(value)?.label || value || '-'
}

function getStatusType(value) {
  return getStatusItem(value)?.type || 'info'
}

function displayValue(value) {
  return value || '-'
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

async function fetchDeviceList() {
  loading.value = true
  try {
    const data = await getDeviceList({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: queryForm.keyword,
      device_type: queryForm.device_type,
      status: queryForm.status
    })
    deviceList.value = data?.items || []
    pagination.total = data?.total || 0
    pagination.page = data?.page || pagination.page
    pagination.page_size = data?.page_size || pagination.page_size
  } catch (error) {
    deviceList.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchDeviceList()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.device_type = ''
  queryForm.status = ''
  pagination.page = 1
  fetchDeviceList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchDeviceList()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchDeviceList()
}

async function openCreateDialog() {
  isEdit.value = false
  currentDeviceId.value = null
  assignForm()
  formDialogVisible.value = true
  await nextTick()
  deviceFormRef.value?.clearValidate()
}

async function openEditDialog(row) {
  try {
    const data = await getDeviceDetail(row.id)
    isEdit.value = true
    currentDeviceId.value = row.id
    assignForm(data || row)
    formDialogVisible.value = true
    await nextTick()
    deviceFormRef.value?.clearValidate()
  } catch (error) {
    ElMessage.error('获取设备详情失败')
  }
}

async function openDetailDialog(row) {
  try {
    detailData.value = await getDeviceDetail(row.id)
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取设备详情失败')
  }
}

async function handleSubmit() {
  const valid = await deviceFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = { ...deviceForm }
    if (isEdit.value) {
      await updateDevice(currentDeviceId.value, payload)
      ElMessage.success('设备修改成功')
    } else {
      await createDevice(payload)
      ElMessage.success('设备新增成功')
    }
    formDialogVisible.value = false
    await fetchDeviceList()
  } catch (error) {
    // request.js already shows backend errors.
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除设备“${row.device_name || row.device_code}”吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteDevice(row.id)
    ElMessage.success('设备删除成功')
    if (deviceList.value.length === 1 && pagination.page > 1) {
      pagination.page -= 1
    }
    fetchDeviceList()
  } catch (error) {
    if (error !== 'cancel') {
      // request.js handles API errors.
    }
  }
}

onMounted(() => {
  fetchDeviceList()
})
</script>

<style scoped>
.device-page {
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
  grid-template-columns: minmax(260px, 1.4fr) minmax(190px, 1fr) minmax(170px, 0.9fr) auto;
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

.device-table {
  width: 100%;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.device-form :deep(.el-select) {
  width: 100%;
}

.device-form :deep(.el-textarea__inner) {
  resize: vertical;
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
