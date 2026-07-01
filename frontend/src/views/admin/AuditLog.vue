<template>
  <div class="audit-log-page">
    <div class="page-header">
      <h2>操作日志审计</h2>
    </div>

    <el-card style="margin-bottom: 16px;">
      <el-form :inline="true" :model="filters">
        <el-form-item label="模块">
          <el-select v-model="filters.module" placeholder="全部" clearable style="width: 160px;" @change="fetchLogs">
            <el-option label="用户管理" value="用户管理" />
            <el-option label="角色管理" value="角色管理" />
            <el-option label="维保审核" value="维保审核" />
            <el-option label="设备管理" value="设备管理" />
            <el-option label="故障处理" value="故障处理" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作">
          <el-select v-model="filters.action" placeholder="全部" clearable style="width: 120px;" @change="fetchLogs">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="审核通过" value="approved" />
            <el-option label="驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="fetchLogs">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="logs" v-loading="loading" stripe border style="width:100%;">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="120" />
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="moduleTag(row.module)">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="actionTag(row.action)">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="250" />
        <el-table-column prop="target_type" label="对象类型" width="120" />
      </el-table>

      <div style="margin-top: 16px; display:flex; justify-content:flex-end;">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="fetchLogs"
        />
      </div>

      <el-empty v-if="!loading && logs.length === 0" description="暂无操作记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const logs = ref([])
const loading = ref(false)

const filters = reactive({ module: '', action: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const moduleTagMap = { '用户管理': 'warning', '角色管理': '', '维保审核': 'info', '设备管理': 'success', '故障处理': 'danger' }
const actionLabelMap = { create: '创建', update: '更新', delete: '删除', approved: '审核通过', rejected: '驳回' }
const actionTagMap = { create: 'success', update: 'warning', delete: 'danger', approved: 'success', rejected: 'danger' }

function moduleTag(module) { return moduleTagMap[module] || '' }
function actionLabel(action) { return actionLabelMap[action] || action }
function actionTag(action) { return actionTagMap[action] || '' }
function formatTime(ts) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('zh-CN')
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filters.module) params.module = filters.module
    if (filters.action) params.action = filters.action

    const res = await request.get('/api/audit-logs', { params })
    logs.value = res?.items || []
    pagination.total = res?.total || 0
  } catch (err) {
    ElMessage.error('获取操作日志失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)
</script>

<style scoped>
.audit-log-page h2 {
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
</style>
