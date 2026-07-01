<template>
  <div class="page-container">
    <el-card>
      <template #header><span>设备信息查看（只读）</span></template>
      <el-table :data="devices" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="device_name" label="设备名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="device_code" label="设备编号" min-width="120" show-overflow-tooltip />
        <el-table-column label="设备类型" min-width="120">
          <template #default="{ row }">
            {{ getDeviceTypeLabel(row.device_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="device_model" label="设备型号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="installation_location" label="安装位置" min-width="150" show-overflow-tooltip />
        <el-table-column prop="maintenance_company" label="维保单位" min-width="150" show-overflow-tooltip />
        <el-table-column prop="responsible_person" label="负责人" min-width="100" />
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
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

    <el-dialog v-model="detailVisible" title="设备详情" width="700px">
      <el-descriptions :column="2" border v-if="currentDevice">
        <el-descriptions-item label="设备编号">{{ currentDevice.device_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentDevice.device_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ getDeviceTypeLabel(currentDevice.device_type) }}</el-descriptions-item>
        <el-descriptions-item label="设备型号">{{ currentDevice.device_model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ currentDevice.installation_location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维保单位">{{ currentDevice.maintenance_company || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ currentDevice.responsible_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentDevice.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDevice.status)" effect="light">
            {{ getStatusLabel(currentDevice.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentDevice.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/api/request'

const statusOptions = [
  { label: '正常', value: 'normal', type: 'success' },
  { label: '维保中', value: 'maintenance', type: 'primary' },
  { label: '故障', value: 'fault', type: 'danger' },
  { label: '停用', value: 'disabled', type: 'info' }
]

const deviceTypeOptions = [
  { label: '曳引电梯', value: 'traction_elevator' },
  { label: '液压电梯', value: 'hydraulic_elevator' },
  { label: '自动扶梯', value: 'escalator' },
  { label: '自动人行道', value: 'moving_walkway' }
]

function getStatusItem(value) {
  return statusOptions.find((item) => item.value === value)
}

function getStatusLabel(value) {
  return getStatusItem(value)?.label || value || '-'
}

function getStatusType(value) {
  return getStatusItem(value)?.type || 'info'
}

function getDeviceTypeLabel(value) {
  return deviceTypeOptions.find((item) => item.value === value)?.label || value || '-'
}

const devices = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentDevice = ref(null)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

async function fetchDevices() {
  loading.value = true
  try {
    const res = await request.get('/api/devices', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size
      }
    })
    devices.value = res?.items || []
    pagination.total = res?.total || 0
  } catch {} finally { loading.value = false }
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchDevices()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchDevices()
}

function showDetail(row) { currentDevice.value = row; detailVisible.value = true }

onMounted(fetchDevices)
</script>

<style scoped>
.page-container { padding: 0; }
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
