<template>
  <div class="page worker-repair-advice">
    <div class="page-header">
      <div>
        <h1>智能检修建议</h1>
        <p>描述现场故障现象，系统将结合本地知识库生成检修辅助建议。</p>
      </div>
    </div>

    <el-card class="input-card" shadow="never">
      <template #header>
        <div class="card-heading">
          <span>故障描述</span>
          <small>请尽量写明设备状态、位置和异常表现</small>
        </div>
      </template>

      <el-input
        v-model="faultDesc"
        type="textarea"
        :rows="5"
        maxlength="1000"
        show-word-limit
        placeholder="例如：电梯停在楼层中间，无法正常开关门"
      />
      <el-button
        class="generate-button"
        type="primary"
        :loading="loading"
        @click="generate"
      >
        生成检修建议
      </el-button>
    </el-card>

    <Transition name="result-reveal">
      <el-card v-if="answer" class="result-card" shadow="never">
        <template #header>
          <div class="result-heading">
            <div class="card-heading">
              <span>检修建议</span>
              <small v-if="recordId">生成记录 ID：{{ recordId }}</small>
            </div>
            <el-button plain size="small" @click="copyAnswer">复制建议</el-button>
          </div>
        </template>

        <div class="advice-content">{{ answer }}</div>
      </el-card>
    </Transition>

    <Transition name="reference-reveal">
      <el-card v-if="references.length" class="reference-card" shadow="never">
        <template #header>
          <div class="card-heading">
            <span>参考知识来源</span>
            <small>{{ references.length }} 条参考片段</small>
          </div>
        </template>

        <el-table :data="references" row-key="chunk_id">
          <el-table-column prop="source_file_name" label="来源文件" min-width="180" show-overflow-tooltip />
          <el-table-column prop="document_type" label="文档类型" min-width="130" />
          <el-table-column prop="chunk_index" label="文本块" width="90" />
          <el-table-column label="相关度" width="100">
            <template #default="{ row }">
              {{ formatScore(row.score) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateRepairAdvice } from '@/api/qa'

const faultDesc = ref('')
const answer = ref('')
const references = ref([])
const recordId = ref(null)
const loading = ref(false)

function formatScore(value) {
  const score = Number(value)
  return Number.isFinite(score) ? score.toFixed(2) : '-'
}

async function generate() {
  const description = faultDesc.value.trim()
  if (!description) {
    ElMessage.warning('请输入故障描述')
    return
  }

  loading.value = true
  answer.value = ''
  references.value = []
  recordId.value = null

  try {
    const data = await generateRepairAdvice({ fault_description: description })
    answer.value = typeof data?.answer === 'string' ? data.answer : ''
    references.value = Array.isArray(data?.references) ? data.references : []
    recordId.value = data?.record_id ?? null

    if (!answer.value) {
      ElMessage.warning('接口未返回可显示的检修建议')
    }
  } catch {
    // request.js 会统一显示后端返回的错误信息。
  } finally {
    loading.value = false
  }
}

async function copyAnswer() {
  try {
    await navigator.clipboard.writeText(answer.value)
    ElMessage.success('检修建议已复制')
  } catch {
    ElMessage.error('复制失败，请手动选择文本复制')
  }
}
</script>

<style scoped>
.worker-repair-advice {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-card,
.result-card,
.reference-card {
  border: 1px solid rgba(20, 83, 45, 0.09);
}

.card-heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-heading > span {
  color: var(--app-text, #17211a);
  font-size: 16px;
  font-weight: 700;
}

.card-heading > small {
  color: var(--app-text-secondary, #6b746e);
  font-size: 12px;
}

.generate-button {
  margin-top: 16px;
}

.result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.advice-content {
  color: var(--app-text, #243028);
  font-size: 14px;
  line-height: 1.85;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  padding: 4px 2px;
}

.result-reveal-enter-active,
.reference-reveal-enter-active {
  transition: opacity 220ms var(--app-ease-out), transform 220ms var(--app-ease-out);
}

.reference-reveal-enter-active {
  transition-delay: 40ms;
}

.result-reveal-leave-active,
.reference-reveal-leave-active {
  transition: opacity 150ms var(--app-ease-out), transform 150ms var(--app-ease-out);
}

.result-reveal-enter-from,
.reference-reveal-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.992);
}

.result-reveal-leave-to,
.reference-reveal-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.995);
}

@media (prefers-reduced-motion: reduce) {
  .result-reveal-enter-active,
  .reference-reveal-enter-active,
  .result-reveal-leave-active,
  .reference-reveal-leave-active {
    transition: opacity 120ms ease-out !important;
    transition-delay: 0ms !important;
  }

  .result-reveal-enter-from,
  .reference-reveal-enter-from,
  .result-reveal-leave-to,
  .reference-reveal-leave-to {
    transform: none !important;
  }
}

@media (max-width: 560px) {
  .result-heading {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
