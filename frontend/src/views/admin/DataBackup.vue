<template>
  <div class="backup-page">
    <div class="page-header">
      <h2>数据备份与恢复</h2>
    </div>

    <el-row :gutter="16">
      <!-- 备份操作区 -->
      <el-col :span="14">
        <el-card>
          <template #header>数据导出</template>
          <p class="desc">将系统数据导出为 JSON 文件保存到本地，用于数据备份或迁移。</p>

          <div class="export-options">
            <el-checkbox-group v-model="exportModules">
              <el-checkbox label="devices">设备数据</el-checkbox>
              <el-checkbox label="faults">故障报告</el-checkbox>
              <el-checkbox label="orders">点检工单</el-checkbox>
              <el-checkbox label="maintenance">维保记录</el-checkbox>
              <el-checkbox label="cases">故障案例</el-checkbox>
              <el-checkbox label="knowledge">知识文件列表</el-checkbox>
              <el-checkbox label="users">用户列表</el-checkbox>
            </el-checkbox-group>
          </div>

          <div style="margin-top: 16px; display: flex; gap: 12px;">
            <el-button type="primary" :loading="exporting" @click="handleExport">
              导出选中数据
            </el-button>
            <el-button :loading="exporting" @click="handleExportAll">
              导出全部数据
            </el-button>
            <el-button :loading="exporting" @click="handleServerExport">
              服务端完整备份
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 统计信息 -->
      <el-col :span="10">
        <el-card>
          <template #header>数据概览</template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="设备数量">{{ stats.device_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="故障报告">{{ stats.fault_report_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="点检工单">{{ stats.inspection_order_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="维保记录">{{ stats.maintenance_record_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="故障案例">{{ stats.repair_case_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="知识文件">{{ stats.knowledge_file_count || '-' }}</el-descriptions-item>
            <el-descriptions-item label="知识切片">{{ stats.knowledge_chunk_count || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 16px;">
          <template #header>数据恢复</template>
          <p class="desc">从之前导出的 JSON 备份文件恢复数据。</p>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".json"
            :on-change="handleFileSelect"
            style="margin-top: 12px;"
          >
            <el-button type="warning">选择备份文件</el-button>
            <template #tip>
              <div style="color:#909399;font-size:12px;margin-top:4px;">
                仅支持本系统导出的 JSON 格式备份文件
              </div>
            </template>
          </el-upload>
          <div style="margin-top: 12px;">
            <el-button
              type="danger"
              :disabled="!selectedFile"
              :loading="importing"
              @click="handleImport"
            >
              开始恢复
            </el-button>
          </div>
          <div v-if="importResult" style="margin-top: 12px;">
            <el-alert
              :title="importResult.message"
              :type="importResult.errors?.length ? 'warning' : 'success'"
              :closable="false"
              show-icon
            />
            <div v-if="importResult.errors?.length" style="margin-top: 8px;">
              <p v-for="(err, i) in importResult.errors" :key="i" style="color:#e6a23c;font-size:12px;">
                {{ err }}
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const exportModules = ref(['devices', 'faults', 'orders', 'maintenance', 'cases', 'knowledge'])
const exporting = ref(false)
const importing = ref(false)
const stats = reactive({})
const selectedFile = ref(null)
const uploadRef = ref(null)
const importResult = ref(null)

// API 到模块映射
const MODULE_APIS = {
  devices: '/api/devices',
  faults: '/api/faults',
  orders: '/api/inspections/orders',
  maintenance: '/api/maintenance/records',
  cases: '/api/cases',
  knowledge: '/api/knowledge/files',
  users: '/api/users'
}

async function fetchStats() {
  try {
    const res = await request.get('/api/dashboard/summary')
    Object.assign(stats, res || {})
  } catch {
    // 静默失败
  }
}

function downloadJSON(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function handleExport() {
  if (exportModules.value.length === 0) {
    ElMessage.warning('请至少选择一个数据模块')
    return
  }
  exporting.value = true
  try {
    const backup = { exported_at: new Date().toISOString(), version: '1.0', data: {} }
    for (const mod of exportModules.value) {
      const url = MODULE_APIS[mod]
      if (!url) continue
      try {
        const res = await request.get(url)
        backup.data[mod] = (res?.items || res || [])
      } catch {
        backup.data[mod] = []
      }
    }
    downloadJSON(backup, `intelligent_maintenance_backup_${new Date().toISOString().slice(0,10)}.json`)
    ElMessage.success('数据导出成功')
  } catch (err) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

async function handleExportAll() {
  exportModules.value = Object.keys(MODULE_APIS)
  await handleExport()
}

async function handleServerExport() {
  exporting.value = true
  try {
    const res = await request.post('/api/backup/export')
    downloadJSON(res, `intelligent_maintenance_full_${new Date().toISOString().slice(0,10)}.json`)
    ElMessage.success('服务端完整备份导出成功')
  } catch (err) {
    ElMessage.error('服务端备份失败')
  } finally {
    exporting.value = false
  }
}

function handleFileSelect(file) {
  selectedFile.value = file
  importResult.value = null
}

async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }
  try {
    await ElMessageBox.confirm(
      '恢复操作将合并导入备份文件中的数据，可能会覆盖已有记录。确定继续？',
      '数据恢复确认',
      { type: 'warning', confirmButtonText: '确认恢复', cancelButtonText: '取消' }
    )
  } catch {
    return
  }

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    const res = await request.post('/api/backup/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    importResult.value = res || {}
    ElMessage.success(res?.message || '数据恢复完成')
  } catch (err) {
    importResult.value = { message: err?.response?.data?.detail || '恢复失败', errors: [] }
    ElMessage.error('数据恢复失败')
  } finally {
    importing.value = false
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.backup-page h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #303133;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.desc {
  color: #606266;
  font-size: 0.9rem;
  margin: 0 0 12px;
  line-height: 1.6;
}

.export-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
}
</style>
