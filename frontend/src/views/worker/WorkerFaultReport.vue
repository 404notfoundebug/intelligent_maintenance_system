<template>
  <div class="page-container">
    <el-card>
      <template #header><span>多模态故障检索</span></template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文字检索" name="text">
          <div style="display:flex;gap:8px;margin-bottom:16px">
            <el-input v-model="textQuery" placeholder="描述故障现象..." style="flex:1" @keyup.enter="searchText" />
            <el-button type="primary" @click="searchText" :loading="loading">检索</el-button>
          </div>
        </el-tab-pane>
        <el-tab-pane label="图片检索" name="image">
          <el-alert title="图片检索需配合后端图像分析服务，当前暂未启用" type="info" :closable="false" show-icon />
        </el-tab-pane>
        <el-tab-pane label="语音输入" name="voice">
          <el-alert title="语音输入功能开发中" type="info" :closable="false" show-icon />
        </el-tab-pane>
      </el-tabs>
      <el-table :data="results" v-loading="loading" stripe style="margin-top:16px">
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="content" label="内容摘要" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ (row.content || row.description || '').slice(0, 80) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !results.length && searched" description="未找到匹配结果" :image-size="80" />
    </el-card>

    <el-dialog v-model="detailVisible" title="检索详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="标题">{{ detailItem.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ detailItem.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ detailItem.source || '知识库' }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ detailItem.content || detailItem.description || '暂无详细内容' }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from '@/api/request'

const activeTab = ref('text')
const textQuery = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const detailVisible = ref(false)
const detailItem = ref({})

async function searchText() {
  if (!textQuery.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await request.post('/api/search', { query: textQuery.value, top_k: 10 })
    results.value = res?.results || res || []
  } catch {
    results.value = []
  } finally { loading.value = false }
}

function showDetail(row) {
  detailItem.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.page-container { padding: 0; }
</style>
