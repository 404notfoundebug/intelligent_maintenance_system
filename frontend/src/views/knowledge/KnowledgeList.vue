<template>
  <div class="page knowledge-page">
    <div class="page-header">
      <div>
        <h1>知识库管理</h1>
        <p>上传、解析和管理维保标准、检修手册、故障案例等知识资料，为检索与RAG建议提供基础内容。</p>
      </div>
      <el-button type="primary" @click="openUploadDialog">上传文档</el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" class="filter-form" label-width="80px">
        <el-form-item label="关键词">
          <el-input
            v-model.trim="queryForm.keyword"
            clearable
            placeholder="请输入文件名或关键词"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-select v-model="queryForm.document_type" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in documentTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="解析状态">
          <el-select v-model="queryForm.parse_status" clearable placeholder="全部">
            <el-option label="全部" value="" />
            <el-option
              v-for="item in parseStatusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openUploadDialog">上传文档</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="fileList"
        row-key="id"
        border
        stripe
        class="knowledge-table"
      >
        <el-table-column prop="id" label="文件ID" width="90" />
        <el-table-column prop="original_filename" label="原始文件名" min-width="200" show-overflow-tooltip />
        <el-table-column label="文档类型" min-width="140">
          <template #default="{ row }">
            {{ getDocumentTypeLabel(row.document_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="文件类型" width="100" />
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column label="解析状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getParseStatusType(row.parse_status)" effect="light">
              {{ getParseStatusLabel(row.parse_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parse_message" label="解析说明" min-width="190" show-overflow-tooltip />
        <el-table-column label="上传时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="230">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetailDialog(row)">查看详情</el-button>
            <el-button link type="primary" @click="openChunksDialog(row)">查看文本块</el-button>
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
      v-model="uploadDialogVisible"
      title="上传知识库文档"
      width="600px"
      destroy-on-close
      @closed="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="文档类型" prop="document_type">
          <el-select v-model="uploadForm.document_type" placeholder="请选择文档类型">
            <el-option
              v-for="item in documentTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件" required>
          <el-upload
            ref="uploadRef"
            v-model:file-list="uploadFileList"
            class="knowledge-upload"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.txt,.docx"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleFileExceed"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击选择</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 pdf、txt、docx 文件，建议单个文件不超过20MB。
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploadLoading" @click="handleUpload">
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="文件详情" width="760px">
      <el-descriptions v-if="detailData" :column="2" border>
        <el-descriptions-item label="文件ID">{{ displayValue(detailData.id) }}</el-descriptions-item>
        <el-descriptions-item label="原始文件名">{{ displayValue(detailData.original_filename) }}</el-descriptions-item>
        <el-descriptions-item label="保存文件名">{{ displayValue(detailData.stored_filename) }}</el-descriptions-item>
        <el-descriptions-item label="文件类型">{{ displayValue(detailData.file_type) }}</el-descriptions-item>
        <el-descriptions-item label="文档类型">{{ getDocumentTypeLabel(detailData.document_type) }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatFileSize(detailData.file_size) }}</el-descriptions-item>
        <el-descriptions-item label="解析状态">
          <el-tag :type="getParseStatusType(detailData.parse_status)" effect="light">
            {{ getParseStatusLabel(detailData.parse_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="文本块数量">{{ displayValue(detailData.chunk_count) }}</el-descriptions-item>
        <el-descriptions-item label="上传时间">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(detailData.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="文件路径" :span="2">
          {{ displayValue(detailData.file_path) }}
        </el-descriptions-item>
        <el-descriptions-item label="解析说明" :span="2">
          {{ displayValue(detailData.parse_message) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog
      v-model="chunksDialogVisible"
      title="文档文本块"
      width="900px"
      class="chunks-dialog"
    >
      <div class="chunks-header" v-if="currentChunkFile">
        <div>
          <strong>{{ currentChunkFile.original_filename }}</strong>
          <span>{{ getDocumentTypeLabel(currentChunkFile.document_type) }}</span>
        </div>
      </div>
      <div v-loading="chunksLoading" class="chunks-body">
        <el-empty v-if="!chunksLoading && chunkList.length === 0" description="暂无文本块" />
        <div v-else class="chunk-list">
          <el-card
            v-for="chunk in chunkList"
            :key="chunk.id"
            class="chunk-card"
            shadow="never"
          >
            <template #header>
              <div class="chunk-card-header">
                <span>文本块 #{{ chunk.chunk_index }}</span>
                <em>{{ chunk.title || '无标题' }}</em>
              </div>
            </template>
            <div class="chunk-content">{{ chunk.content }}</div>
            <div class="chunk-meta">
              <span>metadata_json</span>
              <pre>{{ formatMetadata(chunk.metadata_json) }}</pre>
            </div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <div class="chunk-footer">
          <el-pagination
            v-model:current-page="chunkPagination.page"
            v-model:page-size="chunkPagination.page_size"
            :page-sizes="[5, 10, 20]"
            :total="chunkPagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleChunkSizeChange"
            @current-change="handleChunkCurrentChange"
          />
          <el-button @click="chunksDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  deleteKnowledgeFile,
  getKnowledgeChunks,
  getKnowledgeFileDetail,
  getKnowledgeFiles,
  uploadKnowledgeFile
} from '../../api/knowledge'

const documentTypeOptions = [
  { label: '维保标准', value: 'maintenance_standard' },
  { label: '检修手册', value: 'repair_manual' },
  { label: '故障案例', value: 'fault_case' },
  { label: '点检模板', value: 'inspection_template' },
  { label: '维保记录模板', value: 'maintenance_record_template' }
]

const parseStatusOptions = [
  { label: '待解析', value: 'pending', type: 'warning' },
  { label: '已解析', value: 'parsed', type: 'success' },
  { label: '解析失败', value: 'failed', type: 'danger' }
]

const allowedExtensions = ['pdf', 'txt', 'docx']

const queryForm = reactive({
  keyword: '',
  document_type: '',
  parse_status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const fileList = ref([])
const loading = ref(false)
const uploadDialogVisible = ref(false)
const uploadLoading = ref(false)
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const uploadFileList = ref([])
const selectedFile = ref(null)
const detailDialogVisible = ref(false)
const detailData = ref(null)
const chunksDialogVisible = ref(false)
const chunksLoading = ref(false)
const currentChunkFile = ref(null)
const chunkList = ref([])

const uploadForm = reactive({
  document_type: ''
})

const uploadRules = {
  document_type: [{ required: true, message: '请选择文档类型', trigger: 'change' }]
}

const chunkPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0
})

function getDocumentTypeLabel(value) {
  return documentTypeOptions.find((item) => item.value === value)?.label || value || '-'
}

function getParseStatusItem(value) {
  return parseStatusOptions.find((item) => item.value === value)
}

function getParseStatusLabel(value) {
  return getParseStatusItem(value)?.label || value || '-'
}

function getParseStatusType(value) {
  return getParseStatusItem(value)?.type || 'info'
}

function displayValue(value) {
  return value === 0 ? 0 : value || '-'
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function formatFileSize(size) {
  const bytes = Number(size)
  if (!Number.isFinite(bytes) || bytes < 0) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function formatMetadata(metadata) {
  if (!metadata) return '-'
  if (typeof metadata === 'string') return metadata
  try {
    return JSON.stringify(metadata, null, 2)
  } catch (error) {
    return String(metadata)
  }
}

function getFileExtension(filename = '') {
  return filename.split('.').pop()?.toLowerCase() || ''
}

function isAllowedFile(file) {
  const extension = getFileExtension(file?.name || '')
  return allowedExtensions.includes(extension)
}

async function fetchFileList() {
  loading.value = true
  try {
    const data = await getKnowledgeFiles({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: queryForm.keyword,
      document_type: queryForm.document_type,
      parse_status: queryForm.parse_status
    })
    fileList.value = data?.items || []
    pagination.total = data?.total || 0
    pagination.page = data?.page || pagination.page
    pagination.page_size = data?.page_size || pagination.page_size
  } catch (error) {
    fileList.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchFileList()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.document_type = ''
  queryForm.parse_status = ''
  pagination.page = 1
  fetchFileList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchFileList()
}

function handleCurrentChange(page) {
  pagination.page = page
  fetchFileList()
}

function openUploadDialog() {
  resetUploadForm()
  uploadDialogVisible.value = true
}

function resetUploadForm() {
  uploadForm.document_type = ''
  selectedFile.value = null
  uploadFileList.value = []
  uploadRef.value?.clearFiles()
  uploadFormRef.value?.clearValidate()
}

function handleFileChange(file, fileList) {
  if (!isAllowedFile(file)) {
    ElMessage.warning('仅支持上传 pdf、txt、docx 文件')
    uploadFileList.value = []
    selectedFile.value = null
    return
  }
  const latestFile = fileList[fileList.length - 1]
  uploadFileList.value = latestFile ? [latestFile] : []
  selectedFile.value = latestFile || file
}

function handleFileRemove() {
  selectedFile.value = null
  uploadFileList.value = []
}

function handleFileExceed(files) {
  const latestFile = files[0]
  if (!latestFile || !isAllowedFile(latestFile)) {
    ElMessage.warning('仅支持上传 pdf、txt、docx 文件')
    return
  }
  uploadRef.value?.clearFiles()
  uploadFileList.value = []
  selectedFile.value = null
  uploadRef.value?.handleStart(latestFile)
}

async function handleUpload() {
  const valid = await uploadFormRef.value?.validate().catch(() => false)
  if (!valid) return

  const rawFile = selectedFile.value?.raw
  if (!rawFile) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  if (!isAllowedFile(rawFile)) {
    ElMessage.warning('仅支持上传 pdf、txt、docx 文件')
    return
  }

  const formData = new FormData()
  formData.append('document_type', uploadForm.document_type)
  formData.append('file', rawFile)

  uploadLoading.value = true
  try {
    await uploadKnowledgeFile(formData)
    ElMessage.success('知识库文档上传成功')
    uploadDialogVisible.value = false
    pagination.page = 1
    await fetchFileList()
  } catch (error) {
    // request.js already shows backend errors.
  } finally {
    uploadLoading.value = false
  }
}

async function openDetailDialog(row) {
  try {
    detailData.value = await getKnowledgeFileDetail(row.id)
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取文件详情失败')
  }
}

async function openChunksDialog(row) {
  currentChunkFile.value = row
  chunkPagination.page = 1
  chunkPagination.page_size = 5
  chunkPagination.total = 0
  chunkList.value = []
  chunksDialogVisible.value = true
  await fetchChunks(row.id)
}

async function fetchChunks(fileId = currentChunkFile.value?.id) {
  if (!fileId) return
  chunksLoading.value = true
  try {
    const data = await getKnowledgeChunks(fileId, {
      page: chunkPagination.page,
      page_size: chunkPagination.page_size
    })
    chunkList.value = data?.items || []
    chunkPagination.total = data?.total || 0
    chunkPagination.page = data?.page || chunkPagination.page
    chunkPagination.page_size = data?.page_size || chunkPagination.page_size
  } catch (error) {
    chunkList.value = []
  } finally {
    chunksLoading.value = false
  }
}

function handleChunkSizeChange(size) {
  chunkPagination.page_size = size
  chunkPagination.page = 1
  fetchChunks()
}

function handleChunkCurrentChange(page) {
  chunkPagination.page = page
  fetchChunks()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除知识库文件“${row.original_filename}”吗？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteKnowledgeFile(row.id)
    ElMessage.success('知识库文件删除成功')
    if (fileList.value.length === 1 && pagination.page > 1) {
      pagination.page -= 1
    }
    fetchFileList()
  } catch (error) {
    if (error !== 'cancel') {
      // request.js handles API errors.
    }
  }
}

onMounted(() => {
  fetchFileList()
})
</script>

<style scoped>
.knowledge-page {
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

.knowledge-table {
  width: 100%;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.knowledge-upload {
  width: 100%;
}

.knowledge-upload :deep(.el-upload) {
  width: 100%;
}

.knowledge-upload :deep(.el-upload-dragger) {
  width: 100%;
}

.upload-icon {
  color: #2f6fed;
  font-size: 42px;
  margin-bottom: 8px;
}

.chunks-header {
  padding: 0 0 14px;
  border-bottom: 1px solid #edf1f7;
  margin-bottom: 14px;
}

.chunks-header strong {
  display: block;
  color: #152033;
  font-size: 15px;
  margin-bottom: 4px;
}

.chunks-header span {
  color: #6b778c;
  font-size: 13px;
}

.chunks-body {
  min-height: 260px;
  max-height: 560px;
  overflow-y: auto;
  padding-right: 6px;
}

.chunk-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.chunk-card {
  border: 1px solid #e6edf7;
  border-radius: 10px;
  background: #fbfdff;
}

.chunk-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.chunk-card-header span {
  color: #1f5fbf;
  font-weight: 700;
}

.chunk-card-header em {
  color: #68758a;
  font-style: normal;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chunk-content {
  max-height: 220px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #27364f;
  line-height: 1.7;
  background: #ffffff;
  border: 1px solid #edf1f7;
  border-radius: 8px;
  padding: 12px;
}

.chunk-meta {
  margin-top: 12px;
  color: #68758a;
  font-size: 12px;
}

.chunk-meta span {
  display: block;
  margin-bottom: 6px;
}

.chunk-meta pre {
  max-height: 110px;
  overflow: auto;
  margin: 0;
  padding: 10px;
  border-radius: 8px;
  background: #f3f6fb;
  color: #34445e;
  white-space: pre-wrap;
}

.chunk-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  width: 100%;
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

  .pagination-wrap,
  .chunk-footer {
    justify-content: flex-start;
    overflow-x: auto;
  }
}
</style>
