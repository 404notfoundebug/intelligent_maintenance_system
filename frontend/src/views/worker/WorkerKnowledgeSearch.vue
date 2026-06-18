<template>
  <div class="page-container">
    <el-card>
      <template #header><span>检修知识库查询</span></template>
      <el-input v-model="keyword" placeholder="输入关键词搜索知识库..." @keyup.enter="search" style="margin-bottom:16px">
        <template #append><el-button @click="search" :icon="Search">搜索</el-button></template>
      </el-input>
      <el-table :data="results" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="updated_at" label="更新时间" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !results.length" description="请输入关键词搜索" />
    </el-card>

    <el-dialog v-model="detailVisible" :title="currentDoc?.title" width="700px">
      <div v-if="currentDoc" v-html="currentDoc.content || '暂无内容'"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import request from '@/api/request'

const keyword = ref('')
const results = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentDoc = ref(null)

async function search() {
  if (!keyword.value.trim()) return
  loading.value = true
  try {
    const res = await request.post('/api/search', { query: keyword.value, top_k: 10 })
    results.value = res?.results || res || []
  } catch {} finally { loading.value = false }
}

function showDetail(row) { currentDoc.value = row; detailVisible.value = true }
</script>

<style scoped>
.page-container { padding: 0; }
</style>
