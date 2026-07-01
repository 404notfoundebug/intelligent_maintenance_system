<template>
  <div class="page repair-advice-page">
    <div class="page-header">
      <div>
        <h1>智能检修建议</h1>
        <p>输入设备信息与故障现象，系统将基于知识库检索结果生成标准化检修辅助建议。</p>
      </div>
    </div>

    <div class="advice-layout">
      <el-card class="input-card" shadow="never">
        <template #header>
          <div class="card-title">
            <span>故障输入</span>
            <small>RAG 检修建议生成</small>
          </div>
        </template>

        <el-form :model="form" label-position="top" class="advice-form">
          <el-form-item label="设备名称">
            <el-input
              v-model.trim="form.device_name"
              clearable
              placeholder="请输入设备名称，例如曳引电梯"
            />
          </el-form-item>
          <el-form-item label="设备型号">
            <el-input
              v-model.trim="form.device_model"
              clearable
              placeholder="请输入设备型号，例如TX-1000"
            />
          </el-form-item>
          <el-form-item label="故障现象" required>
            <el-input
              v-model.trim="form.fault_description"
              type="textarea"
              :rows="6"
              maxlength="1000"
              show-word-limit
              placeholder="请输入故障现象，例如：电梯停在层站，不关门"
            />
          </el-form-item>
          <el-form-item label="检索知识片段数量">
            <el-select v-model="form.top_k" placeholder="请选择">
              <el-option
                v-for="item in topKOptions"
                :key="item"
                :label="`${item} 个片段`"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="example-section">
          <div class="section-label">快捷故障示例</div>
          <div class="example-list">
            <el-button
              v-for="example in faultExamples"
              :key="example"
              round
              size="small"
              type="primary"
              plain
              @click="useExample(example)"
            >
              {{ example }}
            </el-button>
          </div>
        </div>

        <div class="action-row">
          <el-button type="primary" :loading="generating" @click="handleGenerate">
            生成检修建议
          </el-button>
          <el-button @click="handleClear">清空</el-button>
        </div>
      </el-card>

      <div class="result-column">
        <el-card class="result-card" shadow="never">
          <template #header>
            <div class="result-header">
              <div class="card-title">
                <span>检修建议</span>
                <small v-if="recordId">生成记录ID：{{ recordId }}</small>
              </div>
              <el-button
                type="primary"
                plain
                size="small"
                :disabled="!answer"
                @click="copyAnswer"
              >
                复制
              </el-button>
            </div>
          </template>

          <div v-if="generating" class="loading-result">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在生成检修建议，请稍候……</span>
          </div>
          <el-empty v-else-if="!answer" description="输入故障现象后，可在此查看生成的检修建议" />
          <div v-else class="answer-content">{{ answer }}</div>
        </el-card>

        <el-card class="reference-card" shadow="never">
          <template #header>
            <div class="card-title">
              <span>参考知识来源</span>
              <small>{{ references.length }} 条参考片段</small>
            </div>
          </template>

          <el-empty v-if="references.length === 0" description="暂无参考来源" />
          <el-table v-else :data="references" border stripe row-key="chunk_id">
            <el-table-column prop="source_file_name" label="来源文件" min-width="180" show-overflow-tooltip />
            <el-table-column label="文档类型" min-width="130">
              <template #default="{ row }">
                {{ getDocumentTypeLabel(row.document_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="chunk_index" label="文本块" width="90" />
            <el-table-column label="相关度" width="100">
              <template #default="{ row }">
                {{ formatScore(row.score) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { generateRepairAdvice } from '../../api/qa'

const topKOptions = [3, 5, 8, 10]

const faultExamples = [
  '电梯停在层站，不关门',
  '扶梯运行时有异响',
  '控制柜显示E35故障码',
  '轿厢门反复开关，无法正常关闭'
]

const documentTypeOptions = [
  { label: '维保标准', value: 'maintenance_standard' },
  { label: '检修手册', value: 'repair_manual' },
  { label: '故障案例', value: 'fault_case' },
  { label: '点检模板', value: 'inspection_template' },
  { label: '维保记录模板', value: 'maintenance_record_template' }
]

const form = reactive({
  device_name: '',
  device_model: '',
  fault_description: '',
  top_k: 5
})

const generating = ref(false)
const answer = ref('')
const references = ref([])
const recordId = ref(null)

function getDocumentTypeLabel(value) {
  return documentTypeOptions.find((item) => item.value === value)?.label || value || '-'
}

function formatScore(value) {
  const score = Number(value)
  return Number.isFinite(score) ? score.toFixed(2) : '-'
}

function useExample(example) {
  form.fault_description = example
}

async function handleGenerate() {
  if (!form.fault_description.trim()) {
    ElMessage.warning('请输入故障现象')
    return
  }

  generating.value = true
  try {
    const data = await generateRepairAdvice({
      device_name: form.device_name.trim(),
      device_model: form.device_model.trim(),
      fault_description: form.fault_description.trim(),
      top_k: form.top_k
    })
    answer.value = data?.answer || ''
    references.value = Array.isArray(data?.references) ? data.references : []
    recordId.value = data?.record_id || null
    ElMessage.success('检修建议生成成功')
  } catch (error) {
    // request.js already displays backend messages, including LLM configuration errors.
  } finally {
    generating.value = false
  }
}

function handleClear() {
  form.device_name = ''
  form.device_model = ''
  form.fault_description = ''
  form.top_k = 5
  answer.value = ''
  references.value = []
  recordId.value = null
}

async function copyAnswer() {
  if (!answer.value) return

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(answer.value)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = answer.value
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'fixed'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}
</script>

<style scoped>
.repair-advice-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.advice-layout {
  display: grid;
  grid-template-columns: minmax(320px, 35%) minmax(0, 65%);
  gap: 18px;
  align-items: start;
}

.input-card,
.result-card,
.reference-card {
  border: 1px solid rgba(30, 92, 180, 0.08);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(16, 41, 84, 0.06);
}

.card-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title span {
  color: #17233d;
  font-size: 16px;
  font-weight: 700;
}

.card-title small {
  color: #7a869a;
  font-size: 12px;
}

.advice-form :deep(.el-select) {
  width: 100%;
}

.advice-form :deep(.el-textarea__inner) {
  line-height: 1.6;
  resize: vertical;
}

.example-section {
  border-top: 1px solid #edf1f7;
  margin-top: 4px;
  padding-top: 16px;
}

.section-label {
  color: #4d5f7a;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-list .el-button {
  margin-left: 0;
  white-space: normal;
  height: auto;
  min-height: 28px;
  line-height: 1.35;
  padding: 6px 12px;
}

.action-row {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.result-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.result-card :deep(.el-card__body) {
  min-height: 360px;
}

.loading-result {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #2f6fed;
  font-size: 15px;
}

.answer-content {
  max-height: 560px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #24324a;
  line-height: 1.8;
  font-size: 14px;
  background: linear-gradient(180deg, #fbfdff 0%, #ffffff 100%);
  border: 1px solid #edf1f7;
  border-radius: 10px;
  padding: 16px;
}

.reference-card :deep(.el-table) {
  width: 100%;
}

@media (max-width: 1180px) {
  .advice-layout {
    grid-template-columns: 1fr;
  }

  .result-card :deep(.el-card__body) {
    min-height: 260px;
  }
}

@media (max-width: 760px) {
  .action-row,
  .result-header {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
