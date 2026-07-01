<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>离线工单缓存</span>
          <div>
            <el-button type="primary" size="small" @click="syncOnline" :loading="syncing">同步在线工单</el-button>
            <el-button size="small" @click="clearCache">清空缓存</el-button>
          </div>
        </div>
      </template>
      <el-alert title="离线缓存说明" type="info" :closable="false" show-icon style="margin-bottom:16px">
        <template #default>
          在网络断开时，可在此页面查看已缓存的工单数据。网络恢复后点击"同步在线工单"将本地修改同步至服务器。
        </template>
      </el-alert>
      <el-empty v-if="!cachedOrders.length" description="暂无缓存工单" :image-size="100" />
      <el-table v-else :data="cachedOrders" stripe>
        <el-table-column prop="id" label="编号" width="60" />
        <el-table-column prop="title" label="工单名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="device_name" label="设备" min-width="120" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.synced ? 'success' : 'warning'">{{ row.synced ? '已同步' : '待同步' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cached_at" label="缓存时间" width="160" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removeItem(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const CACHE_KEY = 'worker_offline_orders'
const cachedOrders = ref([])
const syncing = ref(false)

function loadCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    cachedOrders.value = raw ? JSON.parse(raw) : []
  } catch { cachedOrders.value = [] }
}

function saveCache() {
  localStorage.setItem(CACHE_KEY, JSON.stringify(cachedOrders.value))
}

function removeItem(id) {
  cachedOrders.value = cachedOrders.value.filter(o => o.id !== id)
  saveCache()
  ElMessage.success('已删除')
}

function clearCache() {
  ElMessageBox.confirm('确定清空所有离线缓存？', '确认', { type: 'warning' }).then(() => {
    cachedOrders.value = []
    saveCache()
    ElMessage.success('缓存已清空')
  }).catch(() => {})
}

async function syncOnline() {
  syncing.value = true
  try {
    // 拉取在线工单数据并缓存
    const res = await request.get('/api/inspections/orders?limit=200')
    const orders = res?.items || res || []
    const now = new Date().toLocaleString('zh-CN')
    const synced = (Array.isArray(orders) ? orders : []).slice(0, 30).map(o => ({
      ...o,
      synced: true,
      cached_at: now
    }))
    // 合并已有未同步数据
    const unsynced = cachedOrders.value.filter(o => !o.synced)
    cachedOrders.value = [...unsynced, ...synced]
    saveCache()
    ElMessage.success(`已同步 ${synced.length} 条工单到本地缓存`)
  } catch { ElMessage.error('同步失败，请检查网络连接') } finally { syncing.value = false }
}

onMounted(loadCache)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
