<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识图谱辅助查询</span>
          <el-button type="primary" size="small" @click="fetchData" :loading="loading">刷新图谱</el-button>
        </div>
      </template>
      <div ref="chartRef" style="width:100%;height:550px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import request from '@/api/request'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chart = null
const loading = ref(false)

function buildGraph(files, faults) {
  const nodes = []
  const links = []
  const idMap = {}

  function addNode(id, name, category, symbolSize) {
    if (idMap[id]) return
    idMap[id] = true
    nodes.push({ id, name, category, symbolSize: symbolSize || 30 })
  }

  // 知识文件节点
  ;(files || []).forEach(f => {
    const cat = { pdf: 0, doc: 0, docx: 0, txt: 1, md: 1 }[f.file_type] ?? 2
    addNode(`file_${f.id}`, f.filename || f.title || `文件#${f.id}`, cat, 20 + Math.min((f.chunk_count || 1) * 5, 30))
    if (f.device_type) {
      addNode(`dtype_${f.device_type}`, f.device_type, 3, 25)
      links.push({ source: `file_${f.id}`, target: `dtype_${f.device_type}` })
    }
  })

  // 故障案例节点
  ;(faults || []).forEach(f => {
    const cat = { pending: 5, approved: 6, rejected: 7 }[f.status] ?? 5
    addNode(`fault_${f.id}`, f.title || `案例#${f.id}`, cat, 22)
    if (f.device_name) {
      addNode(`dev_${f.device_name}`, f.device_name, 4, 28)
      links.push({ source: `fault_${f.id}`, target: `dev_${f.device_name}` })
    }
  })

  // 连接同类型节点
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      if (nodes[i].category === nodes[j].category && Math.random() < 0.15) {
        links.push({ source: nodes[i].id, target: nodes[j].id })
      }
    }
  }

  return { nodes, links }
}

function renderGraph(data) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const categories = [
    { name: 'PDF/DOC', itemStyle: { color: '#e74c3c' } },
    { name: 'TXT/MD', itemStyle: { color: '#3498db' } },
    { name: '其他文件', itemStyle: { color: '#95a5a6' } },
    { name: '设备类型', itemStyle: { color: '#2ecc71' } },
    { name: '设备', itemStyle: { color: '#f39c12' } },
    { name: '待审核', itemStyle: { color: '#e67e22' } },
    { name: '已通过', itemStyle: { color: '#27ae60' } },
    { name: '已驳回', itemStyle: { color: '#c0392b' } }
  ]

  chart.setOption({
    tooltip: { formatter: p => p.dataType === 'node' ? `${p.name}<br/>类型: ${categories[p.data.category]?.name || ''}` : '' },
    legend: [{ data: categories.map(c => c.name), bottom: 0 }],
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      categories, data: data.nodes, links: data.links,
      force: { repulsion: 200, edgeLength: [80, 200] },
      label: { show: true, fontSize: 11, formatter: p => p.name.length > 12 ? p.name.slice(0, 11) + '…' : p.name },
      lineStyle: { opacity: 0.3, curveness: 0.1 }
    }]
  })
}

async function fetchData() {
  loading.value = true
  try {
    const [filesRes, faultsRes] = await Promise.all([
      request.get('/api/knowledge/files'),
      request.get('/api/faults')
    ])
    const files = (filesRes?.items || filesRes || [])
    const faults = (faultsRes?.items || faultsRes || [])
    const graph = buildGraph(files, faults)
    renderGraph(graph)
  } catch {
    // 静默
  } finally { loading.value = false }
}

onMounted(fetchData)

onBeforeUnmount(() => { chart?.dispose() })
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
