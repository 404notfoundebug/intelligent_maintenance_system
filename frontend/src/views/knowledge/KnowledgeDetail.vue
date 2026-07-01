<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button text @click="$router.push('/admin/knowledge')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <span>文件详情</span>
        </div>
      </template>

      <div v-if="loading" v-loading="true" style="min-height:200px" />
      <div v-else-if="fileInfo">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ fileInfo.original_filename }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ docTypeMap[fileInfo.document_type] || fileInfo.document_type }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ (fileInfo.file_size / 1024).toFixed(1) }} KB</el-descriptions-item>
          <el-descriptions-item label="解析状态">
            <el-tag :type="statusType(fileInfo.parse_status)">{{ statusText(fileInfo.parse_status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="切片数量">{{ fileInfo.chunk_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ fileInfo.created_at?.slice(0, 19).replace('T', ' ') }}</el-descriptions-item>
          <el-descriptions-item label="解析信息" v-if="fileInfo.parse_message">
            {{ fileInfo.parse_message }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 24px;">
          <el-button @click="$router.push('/admin/knowledge')">返回列表</el-button>
          <el-button type="primary" @click="handleViewChunks">查看切片内容</el-button>
          <el-button type="danger" @click="handleDelete">删除文件</el-button>
        </div>

        <!-- 切片列表 Dialog -->
        <el-dialog v-model="chunksVisible" title="切片内容" width="800px">
          <el-table :data="chunks" v-loading="chunksLoading" stripe max-height="500px">
            <el-table-column prop="chunk_index" label="序号" width="70" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="内容预览" min-width="300">
              <template #default="{ row }">
                <span class="content-preview">{{ row.content?.slice(0, 100) }}{{ row.content?.length > 100 ? '...' : '' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-dialog>
      </div>
      <el-empty v-else description="文件不存在" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const fileInfo = ref(null)
const chunksVisible = ref(false)
const chunks = ref([])
const chunksLoading = ref(false)

const docTypeMap = {
  manual: '维修手册',
  case_book: '故障案例库',
  standard: '国家标准',
  other: '其他'
}

function statusType(s) {
  return { pending: 'warning', parsing: 'warning', done: 'success', error: 'danger' }[s] || 'info'
}
function statusText(s) {
  return { pending: '等待解析', parsing: '解析中', done: '解析完成', error: '解析失败' }[s] || s
}

async function fetchFile() {
  loading.value = true
  try {
    const res = await request.get(`/api/knowledge/files/${route.params.id}`)
    fileInfo.value = res || {}
  } catch {
    ElMessage.error('获取文件信息失败')
  } finally {
    loading.value = false
  }
}

async function handleViewChunks() {
  chunksLoading.value = true
  try {
    const res = await request.get(`/api/knowledge/files/${route.params.id}/chunks`)
    chunks.value = res?.items || res || []
    chunksVisible.value = true
  } catch {
    ElMessage.error('获取切片失败')
  } finally {
    chunksLoading.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确认删除该文件？删除后相关知识将无法检索。', '提示', { type: 'warning' })
    await request.delete(`/api/knowledge/files/${route.params.id}`)
    ElMessage.success('删除成功')
    router.push('/admin/knowledge')
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err?.response?.data?.message || '删除失败')
  }
}

onMounted(fetchFile)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; align-items: center; gap: 12px; }
.content-preview { color: #606266; font-size: 13px; }
</style>
