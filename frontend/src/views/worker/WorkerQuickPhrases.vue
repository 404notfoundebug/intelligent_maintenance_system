<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>常用故障短语快捷输入</span>
          <el-button type="primary" size="small" @click="showAdd">添加短语</el-button>
        </div>
      </template>
      <el-alert title="使用说明" type="info" :closable="false" show-icon style="margin-bottom:16px">
        <template #default>预设常用故障描述短语，在填写工单时可一键复制填入。点击短语可复制到剪贴板。</template>
      </el-alert>
      <el-empty v-if="!phrases.length" description="暂无快捷短语，点击右上角添加" :image-size="80" />
      <el-row :gutter="12" v-else>
        <el-col :span="8" v-for="(p, idx) in phrases" :key="idx" style="margin-bottom:12px">
          <el-card shadow="hover" class="phrase-card" @click="copyPhrase(p)">
            <div class="phrase-content">{{ p.text }}</div>
            <div class="phrase-footer">
              <el-tag size="small" :type="p.category === '电梯' ? 'danger' : 'warning'">{{ p.category }}</el-tag>
              <el-button size="small" type="danger" text @click.stop="removePhrase(idx)">删除</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加快捷短语" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="电梯" value="电梯" />
            <el-option label="扶梯" value="扶梯" />
            <el-option label="通用" value="通用" />
          </el-select>
        </el-form-item>
        <el-form-item label="短语内容">
          <el-input v-model="form.text" type="textarea" :rows="3" placeholder="例如：电梯运行异响，轿厢抖动明显" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addPhrase">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const PHRASES_KEY = 'worker_quick_phrases'
const phrases = ref([])
const dialogVisible = ref(false)
const form = ref({ category: '电梯', text: '' })

const DEFAULTS = [
  { category: '电梯', text: '电梯运行异响，轿厢有明显抖动' },
  { category: '电梯', text: '电梯门开关异常，关门时反复弹开' },
  { category: '电梯', text: '电梯平层不准，轿厢与楼层有较大落差' },
  { category: '扶梯', text: '扶梯运行时有异常摩擦声，梯级晃动' },
  { category: '扶梯', text: '扶梯梳齿板损坏，存在安全隐患' },
  { category: '通用', text: '设备运行正常，完成定期维保检查' }
]

function loadPhrases() {
  try {
    const raw = localStorage.getItem(PHRASES_KEY)
    if (raw) {
      phrases.value = JSON.parse(raw)
    } else {
      phrases.value = [...DEFAULTS]
      savePhrases()
    }
  } catch { phrases.value = [...DEFAULTS] }
}

function savePhrases() {
  localStorage.setItem(PHRASES_KEY, JSON.stringify(phrases.value))
}

function showAdd() {
  form.value = { category: '电梯', text: '' }
  dialogVisible.value = true
}

function addPhrase() {
  if (!form.value.text.trim()) return
  phrases.value.push({ ...form.value })
  savePhrases()
  dialogVisible.value = false
  ElMessage.success('已添加')
}

function removePhrase(idx) {
  phrases.value.splice(idx, 1)
  savePhrases()
  ElMessage.success('已删除')
}

async function copyPhrase(p) {
  try {
    await navigator.clipboard.writeText(p.text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

onMounted(loadPhrases)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.phrase-card { cursor: pointer; transition: all 0.2s; }
.phrase-card:hover { border-color: #409eff; transform: translateY(-2px); }
.phrase-content { font-size: 14px; line-height: 1.6; margin-bottom: 8px; min-height: 44px; }
.phrase-footer { display: flex; justify-content: space-between; align-items: center; }
</style>
