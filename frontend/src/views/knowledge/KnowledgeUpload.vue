<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button text @click="$router.push('/admin/knowledge')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <span>上传知识文件</span>
        </div>
      </template>

      <el-form label-width="100px" style="max-width: 600px; margin: 0 auto;" size="large">
        <el-form-item label="文件类型">
          <el-select v-model="documentType" placeholder="请选择文件类型" style="width:100%">
            <el-option label="维修手册" value="manual" />
            <el-option label="故障案例库" value="case_book" />
            <el-option label="国家标准" value="standard" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :file-list="fileList"
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-button type="primary" plain>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word、TXT、Markdown 格式</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button @click="$router.push('/admin/knowledge')">取消</el-button>
          <el-button type="primary" :loading="uploading" @click="handleUpload">上传并解析</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const uploading = ref(false)
const documentType = ref('manual')
const fileList = ref([])
const selectedFile = ref(null)
const uploadRef = ref(null)

function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw
}

function handleExceed() {
  ElMessage.warning('一次只能上传一个文件')
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('document_type', documentType.value)
    await request.post('/api/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('上传成功，正在解析中')
    router.push('/admin/knowledge')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; align-items: center; gap: 12px; }
</style>
