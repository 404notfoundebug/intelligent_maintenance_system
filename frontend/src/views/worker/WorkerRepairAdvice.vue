<template>
  <div class="page-container">
    <el-card>
      <template #header><span>智能检修建议生成</span></template>
      <el-input v-model="faultDesc" type="textarea" :rows="4" placeholder="请描述故障现象，如：电梯停在层站不关门，无故障代码" />
      <el-button type="primary" :loading="loading" @click="generate" style="margin-top:16px">生成检修建议</el-button>

      <el-card v-if="result" style="margin-top:20px" shadow="hover">
        <template #header><span>检修建议</span></template>
        <div class="advice-content" v-html="renderedAdvice"></div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const faultDesc = ref('')
const result = ref(null)
const loading = ref(false)

const renderedAdvice = computed(() => {
  if (!result.value) return ''
  const r = result.value
  if (r.repair_advice) return r.repair_advice.replace(/\n/g, '<br>')
  return JSON.stringify(r, null, 2)
})

async function generate() {
  if (!faultDesc.value.trim()) { ElMessage.warning('请输入故障描述'); return }
  loading.value = true
  try {
    const res = await request.post('/api/qa/repair-advice', { fault_description: faultDesc.value })
    result.value = res || {}
  } catch { ElMessage.error('生成失败') } finally { loading.value = false }
}
</script>

<style scoped>
.page-container { padding: 0; }
.advice-content { line-height: 1.8; }
</style>
